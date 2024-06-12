use rppal::Gpio;

pub struct Blaster {
    is_blasting: boolean,
    pin: Gpio::OutputPin,
}

impl Blaster {
    fn new(pin_num: u8) -> Self {
        let gpio = Gpio::new()?;
        let pin = gpio.get(pin_num).unwrap().into_output();
        Blaster { 
            is_blasting: false, 
            pin: pin 
        }
    }

    fn fire(&mut self) {
        self.is_blasting = !self.is_blasting;
        if self.is_blasting { self.pin.set_high() } else { self.pin.set_low()};
    }
}