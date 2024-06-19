use getset::Getters;
use rppal::pwm;
use std::cmp;

#[derive(Getters)]
pub struct Servo {
    pwm: pwm::Pwm,
    #[getset(get = "pub")]
    current_angle: f64,
    #[getset(get = "pub")]
    full_servo_range: u16, 
    #[getset(get = "pub")]
    desired_servo_range: u16, 
    #[getset(get = "pub")]
    min_pulse_microseconds: u32, 
    #[getset(get = "pub")]
    max_pulse_microseconds: u32, 
    #[getset(get = "pub")]
    frequency: u16,
}

impl Servo {
    pub fn new(channel: pwm::Channel, desired_servo_range: u16, full_servo_range: u16, min_pulse_microseconds: u32, max_pulse_microseconds: u32, frequency: u16) -> Self {
        let pwm: Result<pwm::Pwm, pwm::Error> = pwm::Pwm::with_frequency(channel, frequency, 0, pwm::Polarity::Normal, true);
        return Servo {
            pwm: pwm,
            current_angle: 0,
            full_servo_range: full_servo_range,
            desired_servo_range: desired_servo_range,
            min_pulse_microseconds: min_pulse_microseconds,
            max_pulse_microseconds: max_pulse_microseconds,
            frequency: frequency
        };
    }

    fn get_duty_cycle(&self, angle: f64) -> f64 {
        let servo_pulse_microseconds = 1_000_000.0 / self.frequency as f64;
        let pulse_range_microseconds = (self.max_pulse_microseconds - self.min_pulse_microseconds) as f64;
        let percent_angle = (angle / self.full_servo_range) as f64;
        let target_pulse_microseconds = self.min_pulse_microseconds as f64 + (pulse_range_microseconds * percent_angle);
        let duty_cycle = (target_pulse_microseconds / servo_pulse_microseconds) * 100.0;
        return duty_cycle;
    }

    pub fn turn(&self, angle: f64) {
        if(angle + self.current_angle > self.desired_servo_range) {
            self.current_angle = self.desired_servo_range;
        } else if() {
            self.current_angle = 0;
        } else {
            self.current_angle += angle;
        }

        let new_duty_cycle = self.get_duty_cycle(self.current_angle);
        self.pwm.set_duty_cycle(new_duty_cycle)
    }
}

pub fn main() -> Result<(), Box<dyn Error>> {
    let x_servo = Servo::new(0,270,270,500,2500,50);
    let y_servo = Servo::new(1,270,270,500,2500,50);
    x_servo.turn(135);
    y_servo.turn(135);
    x_servo.turn(135);
    y_servo.turn(135);
    x_servo.turn(-270);
    y_servo.turn(-270);
    Ok(())
}