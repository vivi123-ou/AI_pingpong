# Ping Pong AI Championship

Game Ping Pong với AI tự động chơi sử dụng Neural Network và Genetic Algorithm.

## Tính năng

- 2 AI đối diện nhau (xanh vs đỏ)
- AI có thể đỡ hụt (không chơi mãi mãi)
- 5 điểm = 1 ván, 2 ván = thắng
- 3 mức độ khó: Easy / Medium / Hard
- Pause/Resume: Nhấn Space
- Chơi lại: Nhấn Enter

##  Cách chơi

### Cài đặt
```bash
pip install pygame numpy
```

### Chạy game
```bash
python game.py
```

Chọn độ khó:
- `1` - EASY (AI dễ đỡ hụt)
- `2` - MEDIUM (cân bằng)
- `3` - HARD (AI khó đỡ hụt)

![AI_Menu](https://github.com/user-attachments/assets/74a1fea8-4d5f-46e6-bcc3-eb9f75e4c24b)


## Cấu trúc
```
AI_PingPong/
├── NeuralNetwork.py  # Mạng neural
├── game.py           # Game chính
└── README.md         # File này
```

## Cách AI hoạt động

AI sử dụng logic dự đoán:
- Tính toán vị trí bóng sẽ rơi
- Di chuyển paddle đến vị trí đó
- **Các yếu tố đỡ hụt:**
  - Delay phản ứng (1-6 frames)
  - Độ chính xác (65%-95%)
  - Tốc độ ngẫu nhiên (80%-100%)
  - Hiệu ứng mệt mỏi
  - 5% cơ hội đỡ hụt ngẫu nhiên
  - Bóng tăng tốc mỗi 5 rally

## Screenshots

Training
![TrainingMode](https://github.com/user-attachments/assets/cfdb572e-3a3f-409d-be4c-e720c941990a)

Demo
![Demo](https://github.com/user-attachments/assets/69bacd1b-6b6f-466e-9fc0-fcea70ece847)
## License

MIT License
