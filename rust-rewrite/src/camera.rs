extern crate opencv;

use opencv::prelude::*;
use opencv::videoio::{VideoCapture, VideoCaptureTrait, CAP_ANY};
use std::error::Error;
use opencv::highgui;
use opencv::imgproc;
use opencv::core::Size;
use opencv::core::Mat;

pub struct Camera {
    fov: f32,
    frame_width: i32,
    frame_height: i32,
    scaled_width: i32,
    scaled_height: i32,
    video: VideoCapture,
}

impl Camera {
    pub fn new(camera_index: i32, fov: f32, frame_width: i32, frame_height: i32, frame_scale_down: i32) -> Result<Self, Box<dyn Error>> {
        let video = VideoCapture::new(camera_index, CAP_ANY)?;
        if !video.is_opened()? {
            return Err(From::from("Failed to open camera"));
        }
        let scaled_width = frame_width / frame_scale_down;
        let scaled_height = frame_height / frame_scale_down;
        Ok(Self {
            fov,
            frame_width,
            frame_height,
            scaled_width,
            scaled_height,
            video,
        })
    }

    pub fn read_video(&mut self) -> Result<opencv::core::Mat, Box<dyn Error>> {
        let mut frame = Mat::default();
        self.video.read(&mut frame)?;
        if frame.empty() {
            return Err(From::from("Failed to read frame"));
        }
        Ok(frame)
    }
}

impl Drop for Camera {
    fn drop(&mut self) {
        self.video.release().unwrap();
    }
}

pub fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create the Camera object
    let mut camera = Camera::new(0, 70.0, 1440, 1080, 8)?;

    loop {
        let frame = camera.read_video()?;
        // Resize frame for display
        let mut display_frame = Mat::default();
        imgproc::resize(&frame, &mut display_frame, Size::new(camera.scaled_width, camera.scaled_height), 0.0, 0.0, imgproc::INTER_LINEAR)?;

        // Display the resulting frame
        highgui::imshow("Frame", &display_frame)?;

        // Break the loop when 'q' is pressed
        if highgui::wait_key(1)? == 'q' as i32 {
            break;
        }
    }
    Ok(())
}
