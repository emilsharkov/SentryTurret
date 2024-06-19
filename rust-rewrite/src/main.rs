mod camera;
mod blaster;
mod servo;
mod turret;

use opencv;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let x_servo = servo::Servo::new(0,90,270,500,2500,50);
    let y_servo = servo::Servo::new(1,180,270,500,2500,50);
    let blaster = blaster::Blaster::new(23);
    let camera = camera::Camera::new(0, 70.0, 1440, 1080, 8);
    let neural_net = opencv::dnn::read_net("../configs/yolov3-tiny.cfg", "../configs/yolov3-tiny.weights")?;
    let classes = turret::Turret::get_classes("../configs/coco.names");
    let turret = turret::Turret::new(blaster,x_servo,y_servo,camera,neural_net,classes);
    turret.start_turret();
    
    Ok(());
}