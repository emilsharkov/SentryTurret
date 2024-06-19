use getset::Getters;
use rppal::Gpio;

#[derive(Getters)]
pub struct Blaster {
    #[getset(get = "pub")]
    is_blasting: bool,
    pin: Gpio::OutputPin,
}

impl Blaster {
    pub fn new(pin_num: u8) -> Self {
        let gpio = Gpio::new()?;
        let pin = gpio.get(pin_num).unwrap().into_output();
        Blaster { 
            is_blasting: false, 
            pin: pin 
        }
    }

    pub fn toggle_shoot(&mut self, is_blasting: bool) {
        self.is_blasting = is_blasting;
        if self.is_blasting { self.pin.set_high() } else { self.pin.set_low()};
    }
}

pub fn main() -> Result<(), Box<dyn Error>> {
    let mut blaster = Blaster::new(23);
    blaster.toggle_shoot(true);
    Ok(())
}