use opencv::{
    core,
    dnn,
    highgui,
    imgproc,
    prelude::*,
    videoio,
    Result,
};
use rppal::pwm::{Pwm, Channel, Polarity};
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

struct Servo {
    gpio_pin: u8,
    pwm: Pwm,
}

impl Servo {
    fn new(gpio_pin: u8) -> Result<Self> {
        let pwm = Pwm::with_channel(Channel::Pwm0)?;
        Ok(Servo { gpio_pin, pwm })
    }

    fn turn(&self, angle: f64) {
        // Logic to turn the servo to the specified angle using PWM
    }
}

struct Blaster {
    gpio_pin: u8,
}

impl Blaster {
    fn new(gpio_pin: u8) -> Self {
        Blaster { gpio_pin }
    }

    fn toggle_shoot(&self, shooting: bool) {
        // Logic to control blaster using GPIO
    }
}

struct Camera {
    fov: f64,
    frame_width: i32,
    frame_height: i32,
    scaled_width: i32,
    scaled_height: i32,
    video: videoio::VideoCapture,
}

impl Camera {
    fn new(camera_index: i32, fov: f64, frame_width: i32, frame_height: i32, frame_scale_down: i32) -> Result<Self> {
        let video = videoio::VideoCapture::new(camera_index, videoio::CAP_ANY)?;
        video.set(videoio::CAP_PROP_FRAME_WIDTH, frame_width as f64)?;
        video.set(videoio::CAP_PROP_FRAME_HEIGHT, frame_height as f64)?;

        if !video.is_opened()? {
            panic!("Unable to open the camera");
        }

        Ok(Self {
            fov,
            frame_width,
            frame_height,
            scaled_width: frame_width / frame_scale_down,
            scaled_height: frame_height / frame_scale_down,
            video,
        })
    }

    fn read_video(&mut self) -> Result<Mat> {
        let mut frame = Mat::default();
        self.video.read(&mut frame)?;
        if frame.size()?.width == 0 {
            Err(opencv::Error::new(0, "Failed to capture frame"))
        } else {
            Ok(frame)
        }
    }
}

struct Turret {
    x_servo: Servo,
    y_servo: Servo,
    blaster: Blaster,
    camera: Camera,
    net: dnn::Net,
}

impl Turret {
    fn new(x_servo: Servo, y_servo: Servo, blaster: Blaster, camera: Camera, net: dnn::Net) -> Self {
        Turret {
            x_servo,
            y_servo,
            blaster,
            camera,
            net,
        }
    }

    fn calculate_turn_angles(&self, target_x: i32, target_y: i32) -> (f64, f64) {
        let x_angle = (target_x as f64 / self.camera.scaled_width as f64) * (self.camera.fov / 2.0);
        let y_angle = (target_y as f64 / self.camera.scaled_height as f64) * (self.camera.fov / 2.0);
        (x_angle, y_angle)
    }

    fn turn_servos(&self, x_angle: f64, y_angle: f64) {
        self.x_servo.turn(x_angle);
        self.y_servo.turn(y_angle);
    }

    fn toggle_shoot(&self, shooting: bool) {
        self.blaster.toggle_shoot(shooting);
    }

    fn process_targets(&self, frame: &mut Mat, boxes: &Vec<core::Rect>, indices: &Vec<i32>, class_ids: &Vec<i32>, confidences: &Vec<f32>, classes: &Vec<String>) -> Result<()> {
        let frame_center_x = self.camera.scaled_width / 2;
        let frame_center_y = self.camera.scaled_height / 2;

        for &i in indices {
            if i != 0 {
                continue;
            }

            let rect = boxes[i as usize];
            let target_x = rect.x + rect.width / 2;
            let target_y = rect.y + rect.height / 2;
            let label = &classes[class_ids[i as usize] as usize];
            let confidence = confidences[i as usize];

            let target_color = if (frame_center_x - 20..=frame_center_x + 20).contains(&target_x) &&
                                  (frame_center_y - 20..=frame_center_y + 20).contains(&target_y) {
                self.toggle_shoot(true);
                (0, 255, 0)
            } else {
                self.toggle_shoot(false);
                (0, 0, 255)
            };

            let (x_angle, y_angle) = self.calculate_turn_angles(target_x, target_y);
            self.turn_servos(x_angle, y_angle);

            imgproc::circle(frame, core::Point::new(target_x, target_y), 10, core::Scalar::new(target_color.0 as f64, target_color.1 as f64, target_color.2 as f64, 0.0), -1, 8, 0)?;
            imgproc::rectangle(frame, rect, core::Scalar::new(0.0, 255.0, 0.0, 0.0), 2, 8, 0)?;
            imgproc::put_text(frame, &format!("{} {:.2}", label, confidence), core::Point::new(rect.x, rect.y - 10), imgproc::FONT_HERSHEY_SIMPLEX, 0.5, core::Scalar::new(0.0, 255.0, 0.0, 0.0), 2, imgproc::LINE_AA, false)?;
        }

        Ok(())
    }

    fn process_frame(&mut self, frame: &mut Mat, output_layers: &Vec<String>, conf_threshold: f32, nms_threshold: f32) -> Result<(Vec<core::Rect>, Vec<i32>, Vec<i32>, Vec<f32>)> {
        let mut blob = Mat::default();
        dnn::blob_from_image(&frame, &mut blob, 0.00392, core::Size::new(self.camera.scaled_width, self.camera.scaled_width), core::Scalar::new(0.0, 0.0, 0.0, 0.0), true, false)?;
        self.net.set_input(&blob, "", 1.0, core::Scalar::new(0.0, 0.0, 0.0, 0.0))?;

        let mut outs = core::Vector::new();
        self.net.forward(&mut outs, &output_layers)?;

        let mut class_ids = Vec::new();
        let mut confidences = Vec::new();
        let mut boxes = Vec::new();

        for out in outs {
            let data = out.data_typed::<f32>()?;
            for i in (0..out.total()? as usize).step_by(85) {
                let confidence = data[i + 4];
                if confidence > conf_threshold {
                    let center_x = (data[i] * self.camera.scaled_width as f32) as i32;
                    let center_y = (data[i + 1] * self.camera.scaled_height as f32) as i32;
                    let width = (data[i + 2] * self.camera.scaled_width as f32) as i32;
                    let height = (data[i + 3] * self.camera.scaled_height as f32) as i32;
                    let x = center_x - width / 2;
                    let y = center_y - height / 2;

                    boxes.push(core::Rect::new(x, y, width, height));
                    confidences.push(confidence);
                    class_ids.push(data[i + 5..i + 85].iter().cloned().enumerate().max_by(|a, b| a.1.partial_cmp(&b.1).unwrap()).unwrap().0 as i32);
                }
            }
        }

        let indices = dnn::nms_boxes(&boxes, &confidences, conf_threshold, nms_threshold, 0.0, 0)?;

        Ok((boxes, indices, class_ids, confidences))
    }

    fn get_classes() -> Vec<String> {
        let path = Path::new("../configs/coco.names");
        let file = File::open(&path).expect("Could not open coco.names file");
        let reader = io::BufReader::new(file);

        reader.lines().map(|l| l.expect("Could not parse line")).collect()
    }

    fn get_output_layers(&self) -> Vec<String> {
        let layer_names = self.net.get_layer_names().unwrap();
        let unconnected_out_layers = self.net.get_unconnected_out_layers().unwrap();
        unconnected_out_layers.iter().map(|&i| layer_names[i as usize - 1].clone()).collect()
    }
}

fn main() -> Result<()> {
    let x_servo = Servo::new(17)?;
    let y_servo = Servo::new(24)?;
    let blaster = Blaster::new(23);
    let mut camera = Camera::new(0, 70.0, 1440, 1080, 8)?;
    let net = dnn::read_net_from_darknet("../configs/yolov3-tiny.cfg", "../configs/yolov3-tiny.weights")?;

    let turret = Turret::new(x_servo, y_servo, blaster, camera, net);

    let output_layers = turret.get_output_layers();
    let classes = Turret::get_classes();

    loop {
        let mut frame = Mat::default();
        turret.camera.video.read(&mut frame)?;

        let (boxes, indices, class_ids, confidences) = turret.process_frame(&mut frame, &output_layers, 0.5, 0.4)?;
        turret.process_targets(&mut frame, &boxes, &indices, &class_ids, &confidences, &classes)?;

        highgui::imshow("People Detection", &frame)?;

        if highgui::wait_key(1)? == 'q' as i32 {
            break;
        }
    }

    highgui::destroy_all_windows()?;
    Ok(())
}
