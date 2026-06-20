package com.example.vnpay_hub;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class VnpayHubApplication {

	public static void main(String[] args) {
		// 1. Lấy đường dẫn file .env từ VM Options đã cấu hình ở IntelliJ
		String envFilePath = System.getProperty("env.file.path");

		if (envFilePath != null) {
			// Tách đường dẫn thành thư mục và tên file để thư viện dotenv xử lý
			java.io.File file = new java.io.File(envFilePath);
			if (file.exists()) {
				Dotenv dotenv = Dotenv.configure()
						.directory(file.getParent()) // Thư mục chứa file (D:/vnpay)
						.filename(file.getName())    // Tên file (.env)
						.load();

				// Nạp từng biến trong file .env vào System Properties của Spring Boot
				dotenv.entries().forEach(entry ->
						System.setProperty(entry.getKey(), entry.getValue())
				);
			}
		}

		// 2. Chạy ứng dụng Spring Boot như bình thường
		SpringApplication.run(VnpayHubApplication.class, args);
	}
}