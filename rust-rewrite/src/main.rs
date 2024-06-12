mod camera;
mod blaster;
mod servo;

use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    camera::main()
}