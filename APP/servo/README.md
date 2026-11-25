# APP 层：SG90 舵机保护

`app::ServoApp` 是舵机的**应用层保护壳**，不直接碰 PWM，也不做角度换算。

```text
APP/ServoApp
  │ 只依赖 module::IServo
  ▼
module::Sg90Servo
  │ 角度→脉宽
  ▼
bsp_sg90（C）
```

## 文件

```text
APP/servo/
├─ servo_app.hpp
├─ servo_app.cpp
└─ README.md
```

## 保护内容

| 保护 | 行为 |
|---|---|
| 软限位 | 只接受 `[min_angle_deg, max_angle_deg]` |
| 斜率限制 | 按 `max_speed_deg_per_s` 逐步逼近，不猛甩 |
| 命令超时 | 超过 `command_timeout_ms` 没新命令，回 `safe_angle_deg` |
| 连续错误 | 连续 `max_consecutive_errors` 次失败，进入 `Fault` |
| 故障回安全角 | `enterFault()` 尝试回安全角 |
| 急停 | `emergencyStop()` 关闭 PWM，锁存 `EStopped` |
| 故障恢复 | `clearFault()` 从 `Fault` 回安全角并恢复 `Ready` |

## 状态机

```text
Init ──init()──► Ready ──setTarget()──► Moving
                    ▲                      │
                    └──────到达目标────────┘
                    │
                    ├──超时──► Safe ──setTarget()──► Moving
                    │
                    └──连续错误──► Fault ──clearFault()──► Ready
                                      │
                                      └──emergencyStop()──► EStopped
```

- `EStopped` 只能复位/重新上电恢复；
- `Fault` 可以 `clearFault()` 恢复；
- `Safe` 不是故障，只是超时回安全角。

## 配置

```cpp
struct ServoConfig {
    float min_angle_deg{15.0f};
    float max_angle_deg{165.0f};
    float safe_angle_deg{90.0f};
    float max_speed_deg_per_s{120.0f};
    std::uint32_t command_timeout_ms{500u};
    std::uint8_t max_consecutive_errors{3u};
};
```

建议：

- 机械行程 0..180 时，软限位先设 15..165；
- `safe_angle_deg` 设中位 90；
- `max_speed_deg_per_s` 先 120，再按舵机负载调；
- `command_timeout_ms` 500ms 适合手动/遥控，自动控制可更短；
- `max_consecutive_errors` 3 次。

## 用法

```cpp
#include "servo/sg90_servo.hpp"
#include "servo/servo_app.hpp"

static module::Sg90Servo servo1(module::ServoChannel::Ch1);

static app::ServoApp servo_app(
    servo1,
    app::ServoConfig{
        15.0f,   // min
        165.0f,  // max
        90.0f,   // safe
        120.0f,  // deg/s
        500u,    // timeout ms
        3u       // errors
    });

void app_init()
{
    if (!servo_app.init(HAL_GetTick())) {
        Error_Handler();
    }
}

void app_tick_10ms()
{
    servo_app.update(HAL_GetTick());
}

void on_button()
{
    if (!servo_app.setTarget(45.0f, HAL_GetTick())) {
        // 越界/状态不允许
    }
}

void on_estop()
{
    servo_app.emergencyStop();
}
```

`now_ms` 由调用方传入，`ServoApp` 自己不调用 `HAL_GetTick()`，方便做 host 测试。

## 关键行为

### 1. 命令越界

```cpp
servo_app.setTarget(200.0f, now); // false
```

不会自动夹到 165，而是拒绝。  
要不要 clamp 由更上层决定。

### 2. 超时回安全角

```text
最后命令 0ms
500ms 后目标自动变成 90°
以 max_speed 逐步回中，不瞬间跳
状态进入 Safe
```

### 3. 连续错误

```text
setAngle 失败 → error_count++
连续 3 次失败 → Fault
Fault 时 update() 不再输出
clearFault() 尝试回安全角
```

### 4. 急停

```cpp
servo_app.emergencyStop();
```

- 立即停止 PWM；
- 状态 `EStopped`；
- `init()` / `clearFault()` 都不恢复；
- 需要复位/重新上电。

## 为什么放在 APP

| 层 | 职责 |
|---|---|
| BSP | TIM2、CCR、50Hz |
| Module | 角度→脉宽、标定 |
| APP | 限位、斜率、超时、故障、急停 |

保护策略会随应用变化（例如抓取机构和平移机构安全角不同），所以不放在 BSP/module。

## CMake

```cmake
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    APP/servo/servo_app.cpp
)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    APP
    module
    bsp
)
```

## 注意

- `update()` 必须周期调用（建议 10ms），否则超时/斜率保护不会生效；
- `setTarget()` 只设置目标，不立即输出；真正的输出在 `update()`；
- `init()` 会直接回安全角，第一次上电可能看到舵机回中；
- 急停后不要用 `clearFault()` 强行恢复；
- 机械限位开关应作为最后一道保护，软件限位不能替代硬件限位。
