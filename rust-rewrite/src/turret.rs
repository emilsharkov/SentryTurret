use opencv;
use crate::blaster::Blaster;
use crate::servo::Servo;
use crate::camera::Camera;
pub struct Turret {
    blaster: Blaster,
    x_servo: Servo,
    y_servo: Servo,
    camera: Camera,
    neural_net: opencv::dnn::Net,
    classes: Vec<String>
}

impl Turret {
    pub fn new(blaster: Blaster, x_servo: Servo, y_servo: Servo, camera: Camera, neural_net: opencv::dnn::Net, classes: Vec<String>) -> Self {
        return Turret {
            blaster: blaster,
            x_servo: x_servo,
            y_servo: y_servo,
            camera: camera,
            neural_net: neural_net,
            classes: classes
        };
    }

    fn calculate_turn_angle_from_camera(&self, target_x: u16, target_y: u16) -> (f64,f64) {
        let x_angle = (target_x / self.camera.scaled_width()) as f64 * (self.camera.fov() / 2) as f64;
        let y_angle = (target_y / self.camera.scaled_height()) as f64 * (self.camera.fov() / 2) as f64;
        return (x_angle,y_angle);
    }

    fn turn_servos(&self, x_angle: f64, y_angle: f64) {
        self.x_servo.turn(x_angle);
        self.y_servo.turn(y_angle);
    }

    pub fn get_classes(path: &String) -> Vec<String> {
        let path = Path::new(path);
        let file = File::open(&path).unwrap();
        io::BufReader::new(file).lines().map(|line| line.unwrap()).collect()
    }

    fn get_output_layers(&self) -> Vector<String> {
        let layer_names = self.net.get_layer_names().unwrap();
        let unconnected_out_layers = self.net.get_unconnected_out_layers().unwrap();
        return unconnected_out_layers.iter().map(|&i| layer_names.get(i as usize - 1).unwrap().to_string()).collect();
    }

    fn process_targets(&self, frame: &mut Mat, boxes: &Vec<Rect>, indices: &Vector<i32>, classes: &Vec<String>, class_ids: &Vec<i32>, confidences: &Vec<f32>) {
        let frame_center_x = self.camera.scaled_width() / 2;
        let frame_center_y = self.camera.scaled_height() / 2;

        for &i in indices {
            if i != 0 {
                return;
            }

            let box_ = boxes[i as usize];
            let label = &classes[class_ids[i as usize] as usize];
            let confidence = confidences[i as usize];

            // Draw bounding box and label
            let target_x = box_.x + box_.width / 2;
            let target_y = box_.y + box_.height / 2;
            let mut target_color = Scalar::new(0.0, 0.0, 255.0, 0.0);

            if (frame_center_x - 20..=frame_center_x + 20).contains(&target_x) && (frame_center_y - 20..=frame_center_y + 20).contains(&target_y) {
                target_color = Scalar::new(0.0, 255.0, 0.0, 0.0);
                // self.toggle_shoot(true);
            } else {
                self.toggle_shoot(false);
            }

            let (x_angle, y_angle) = self.calculate_turn_angles(target_x, target_y);
            // self.turn_servos(x_angle, y_angle);
            println!("{}, {}", x_angle, y_angle);

            imgproc::circle(frame, Point::new(target_x, target_y), 10, target_color, -1, imgproc::LINE_8, 0).unwrap();
            imgproc::rectangle(frame, box_, Scalar::new(0.0, 255.0, 0.0, 0.0), 2, imgproc::LINE_8, 0).unwrap();
            imgproc::put_text(frame, &format!("{} {:.2}", label, confidence), Point::new(box_.x, box_.y - 10), imgproc::FONT_HERSHEY_SIMPLEX, 0.5, Scalar::new(0.0, 255.0, 0.0, 0.0), 2, imgproc::LINE_8, false).unwrap();
        }
    }

    fn process_frame(&self, frame: &mut Mat, output_layers: &Vector<String>, conf_threshold: f32, nms_threshold: f32) -> (Mat, Vec<Rect>, Vector<i32>, Vec<i32>, Vec<f32>) {
        let mut frame = imgproc::resize(frame, Size::new(self.camera.scaled_width(), self.camera.scaled_height()), 0.0, 0.0, imgproc::INTER_LINEAR).unwrap();
        let (height, width) = (frame.rows(), frame.cols());

        // Detect objects
        let mut blob = Mat::default();
        dnn::blob_from_image(&frame, &mut blob, 0.00392, Size::new(self.camera.scaled_width(), self.camera.scaled_width()), Scalar::new(0.0, 0.0, 0.0, 0.0), true, false).unwrap();
        self.net.set_input(&blob, "", 1.0, Scalar::new(0.0, 0.0, 0.0, 0.0)).unwrap();
        let mut outs = Vector::new();
        self.net.forward(&mut outs, output_layers).unwrap();

        // Process detections
        let mut class_ids = Vec::new();
        let mut confidences = Vec::new();
        let mut boxes = Vec::new();
        for out in outs.iter() {
            let out = out.downcast_ref::<Mat>().unwrap();
            for j in 0..out.rows() {
                let detection = out.row(j).unwrap();
                let detection = detection.to_mat().unwrap();
                let scores = &detection.at(5).unwrap().to_vec();
                let class_id = scores.iter().enumerate().max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(i, _)| i).unwrap() as i32;
                let confidence = scores[class_id as usize];

                if confidence > conf_threshold && class_id == 0 {
                    let center_x = (detection.at(0).unwrap() * width as f32) as i32;
                    let center_y = (detection.at(1).unwrap() * height as f32) as i32;
                    let w = (detection.at(2).unwrap() * width as f32) as i32;
                    let h = (detection.at(3).unwrap() * height as f32) as i32;

                    let x = center_x - w / 2;
                    let y = center_y - h / 2;

                    boxes.push(Rect::new(x, y, w, h));
                    confidences.push(confidence);
                    class_ids.push(class_id);
                }
            }
        }

        // Apply non-maximum suppression to eliminate redundant overlapping boxes
        let indices = dnn::nms_boxes(&boxes, &confidences, conf_threshold, nms_threshold, &Vector::default(), 1.0, 0).unwrap();

        imgproc::circle(&mut frame, Point::new(width / 2, height / 2), 10, Scalar::new(0.0, 0.0, 255.0, 0.0), -1, imgproc::LINE_8, 0).unwrap();

        (frame, boxes, indices, class_ids, confidences)
    }

    pub fn start_turret(&self) {
        let output_layers = self.get_output_layers();
        let classes = self.classes;

        loop {
            let frame = self.camera.read_video()?;
            let (mut frame, boxes, indices, class_ids, confidences) = turret.process_frame(&mut frame, &output_layers, 0.5, 0.4);
            turret.process_targets(&mut frame, &boxes, &indices, &classes, &class_ids, &confidences);
            
            highgui::imshow("Frame", &display_frame)?;
            if highgui::wait_key(1)? == 'q' as i32 {
                break;
            }
        }
        Ok(())
    }
}