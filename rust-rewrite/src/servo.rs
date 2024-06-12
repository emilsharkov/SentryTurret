use rppal::pwm;

pub struct Servo {
    pwm: pwm::Pwm,
    current_angle: u16,
    desired_servo_range: u16, 
    full_servo_range: u16, 
    min_pulse_microseconds: u32, 
    max_pulse_microseconds: u32, 
    frequency: u16,
}

impl Servo {
    fn new(channel: pwm::Channel, desired_servo_range: u16, full_servo_range: u16, min_pulse_microseconds: u32, max_pulse_microseconds: u32, frequency: u16) -> Self {
        let pwm = 
        Servo {

        }
    }
}