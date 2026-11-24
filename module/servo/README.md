# SG90 角度—脉宽算法

角度换算放在 **module 层**，BSP 只负责输出脉宽。

```text
app
 │ Sg90Servo::setAngle(deg)
 ▼
module/servo/sg90_angle.cpp   ← 角度→脉宽算法
 │ bsp_sg90_set_pulse_us(pulse)
 ▼
bsp/pwm/bsp_sg90.c            ← TIM2 CCR，输出 50Hz PWM
```

## 文件

```text
module/servo/
├─ sg90_angle.hpp     # Sg90Calibration + 换算函数
├─ sg90_angle.cpp     # 线性插值实现
├─ sg90_servo.hpp     # Sg90Servo
├─ sg90_servo.cpp     # 调角度换算 + C BSP
└─ README.md
```

## 标定参数

```cpp
struct Sg90Calibration {
    float min_angle_deg{0.0f};
    float max_angle_deg{180.0f};
    std::uint16_t min_pulse_us{500u};
    std::uint16_t max_pulse_us{2500u};
};
```

默认按常见 SG90：

```text
0°   ↔ 500us
180° ↔ 2500us
```

但每个舵机有机械误差，**建议实测**：

1. 先给 1500us，确认中位；
2. 慢慢减到舵机刚到 0° 不堵转，记下 `min_pulse_us`；
3. 慢慢加到 180° 不堵转，记下 `max_pulse_us`；
4. 用这两个值构造 `Sg90Calibration`。

## 算法

线性插值：

```text
ratio = (deg - min_angle_deg) / (max_angle_deg - min_angle_deg)
pulse = min_pulse_us + ratio × (max_pulse_us - min_pulse_us)
```

然后四舍五入到最近的微秒：

```cpp
pulse = static_cast<uint16_t>(pulse_f + 0.5f);
```

代码在 [sg90_angle.cpp](sg90_angle.cpp)：

```cpp
const float angle_span = cal.max_angle_deg - cal.min_angle_deg;
const float pulse_span =
    static_cast<float>(cal.max_pulse_us - cal.min_pulse_us);
const float ratio = (deg - cal.min_angle_deg) / angle_span;
const float pulse_f =
    static_cast<float>(cal.min_pulse_us) + ratio * pulse_span;
```

反算：

```text
ratio = (pulse - min_pulse_us) / (max_pulse_us - min_pulse_us)
deg = min_angle_deg + ratio × (max_angle_deg - min_angle_deg)
```

## 示例计算

默认标定：

| 角度 | 计算 | 脉宽 |
|---:|---|---:|
| 0° | 500 + 0 | 500us |
| 45° | 500 + 0.25×2000 | 1000us |
| 90° | 500 + 0.5×2000 | 1500us |
| 135° | 500 + 0.75×2000 | 2000us |
| 180° | 500 + 1.0×2000 | 2500us |

## 用法

```cpp
#include "servo/sg90_servo.hpp"

// 默认标定
static module::Sg90Servo servo1(module::ServoChannel::Ch1);

// 自定义标定：例如实测 0°=600us，180°=2400us
static module::Sg90Servo servo2(
    module::ServoChannel::Ch2,
    module::Sg90Calibration{0.0f, 180.0f, 600u, 2400u});

void app_init()
{
    servo1.init();
    servo2.init();

    servo1.setAngle(90.0f);  // -> 1500us
    servo2.setAngle(90.0f);  // -> 1500us
}
```

`Sg90Calibration` 的字段顺序：

```text
min_angle_deg, max_angle_deg, min_pulse_us, max_pulse_us
```

C++17 下用聚合初始化，不要用 C++20 的 designated initializer。

## 错误处理

```cpp
auto st = servo.setAngle(200.0f);
if (st != module::ServoStatus::Ok) {
    // InvalidArgument：角度越界或标定非法
}
```

- `Sg90Calibration::valid()` 检查：
  - `max_angle > min_angle`；
  - `min_pulse >= 500`；
  - `max_pulse <= 2500`；
  - `max_pulse > min_pulse`。
- 角度超出 `[min_angle, max_angle]`：`InvalidArgument`；
- 标定非法：`init()` 返回 `InvalidArgument`；
- BSP 未初始化：`NotReady`。

## 为什么放在 module

| 层 | 该做什么 |
|---|---|
| BSP | TIM2、CCR、50Hz、脉宽 |
| Module | 角度→脉宽、标定、限幅、单位 |
| App | 业务角度/动作 |

这样换舵机型号时，只改 `Sg90Calibration`，不用改 BSP 的 PWM 配置。
