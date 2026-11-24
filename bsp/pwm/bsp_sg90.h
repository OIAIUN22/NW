/**
  ******************************************************************************
  * @file    bsp_sg90.h
  * @brief   SG90 舵机 PWM 驱动（BSP 层）
  *
  * 只负责：
  *   - 初始化 TIM2 CH1/CH2 为 50Hz PWM；
  *   - 设置脉宽（500..2500us）；
  *   - 停止某个通道。
  *
  * 角度—脉宽换算在 module/servo/sg90_angle，不在 BSP。
  *
  * 不负责：
  *   - 舵机电源管理（SG90 必须 5V 独立供电，和 MCU 共地）；
  *   - 机械限位/电流保护（上层要限幅、缓动）；
  *   - 编码器/闭环控制。
  *
  * 引脚：
  *   PA0 = TIM2_CH1 → SG90 #1 信号
  *   PA1 = TIM2_CH2 → SG90 #2 信号
  *
  * 注意：
  *   本驱动自己初始化 TIM2，不要再用 CubeMX 重复配置 TIM2。
  ******************************************************************************
  */

#ifndef BSP_SG90_H
#define BSP_SG90_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BSP_SG90_MIN_PULSE_US 500u
#define BSP_SG90_MAX_PULSE_US 2500u
#define BSP_SG90_CENTER_US    1500u

typedef enum {
    BSP_SG90_CH1 = 0,   /* PA0 / TIM2_CH1 */
    BSP_SG90_CH2 = 1,   /* PA1 / TIM2_CH2 */
} bsp_sg90_channel_t;

typedef enum {
    BSP_SG90_OK = 0,
    BSP_SG90_ERR_PARAM,
    BSP_SG90_ERR_INIT,
    BSP_SG90_ERR_BUSY,
    BSP_SG90_ERR_STATE,
} bsp_sg90_status_t;

/**
  * @brief  初始化 TIM2 CH1/CH2 为 50Hz PWM，两个通道回中位 1500us
  * @retval BSP_SG90_OK        成功
  * @retval BSP_SG90_ERR_INIT  HAL 初始化/启动失败
  * @retval BSP_SG90_ERR_BUSY  已经初始化
  */
bsp_sg90_status_t bsp_sg90_init(void);

/**
  * @brief  设置脉宽
  * @param  ch  通道
  * @param  us  脉宽，500..2500us
  */
bsp_sg90_status_t bsp_sg90_set_pulse_us(bsp_sg90_channel_t ch,
                                        uint16_t us);

/**
  * @brief  停止某个通道的 PWM 输出
  */
bsp_sg90_status_t bsp_sg90_disable(bsp_sg90_channel_t ch);

/**
  * @brief  是否已初始化
  */
uint8_t bsp_sg90_is_ready(void);

#ifdef __cplusplus
}
#endif

#endif /* BSP_SG90_H */
