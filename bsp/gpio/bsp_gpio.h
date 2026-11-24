/**
  ******************************************************************************
  * @file    bsp_gpio.h
  * @brief   STM32F1 GPIO 纯驱动（BSP 层）
  *
  * 这一层只负责“把 HAL 的 GPIO 操作变成项目内可复用的驱动”：
  *   - 不包含 LED、按键、业务逻辑；
  *   - 不依赖 FreeRTOS / module / app；
  *   - 每个实例保存自己的 port/pin，可创建多个 GPIO 对象。
  *
  * 约定：
  *   - 本文件属于 BSP 层，可以包含 HAL 头文件；
  *   - module/app 不应直接包含本文件，只通过 board 配置/组合根使用。
  ******************************************************************************
  */

#ifndef BSP_GPIO_H
#define BSP_GPIO_H

#include <stdint.h>

#include "stm32f1xx_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Exported types ------------------------------------------------------------*/

typedef enum {
    BSP_GPIO_OK = 0,
    BSP_GPIO_ERR_PARAM,
    BSP_GPIO_ERR_PORT,
    BSP_GPIO_ERR_STATE,
} bsp_gpio_status_t;

typedef enum {
    BSP_GPIO_MODE_INPUT = 0,
    BSP_GPIO_MODE_OUTPUT_PP,
    BSP_GPIO_MODE_OUTPUT_OD,
    BSP_GPIO_MODE_ANALOG,
} bsp_gpio_mode_t;

typedef enum {
    BSP_GPIO_PULL_NONE = 0,
    BSP_GPIO_PULL_UP,
    BSP_GPIO_PULL_DOWN,
} bsp_gpio_pull_t;

typedef enum {
    BSP_GPIO_SPEED_LOW = 0,
    BSP_GPIO_SPEED_MEDIUM,
    BSP_GPIO_SPEED_HIGH,
} bsp_gpio_speed_t;

typedef enum {
    BSP_GPIO_LOW = 0,
    BSP_GPIO_HIGH = 1,
} bsp_gpio_level_t;

/**
  * @brief  GPIO 初始化配置
  *
  * @note   port/pin 使用 HAL 的 GPIOx / GPIO_PIN_x，例如：
  *         { .port = GPIOC, .pin = GPIO_PIN_13, ... }
  */
typedef struct {
    GPIO_TypeDef *port;             /**< GPIOA / GPIOB / GPIOC ... */
    uint16_t pin;                   /**< GPIO_PIN_0 ... GPIO_PIN_15 的位掩码 */
    bsp_gpio_mode_t mode;           /**< 输入/推挽/开漏/模拟 */
    bsp_gpio_pull_t pull;           /**< 上拉/下拉/无 */
    bsp_gpio_speed_t speed;         /**< 输出速度 */
    bsp_gpio_level_t initial;       /**< 输出模式下的初始电平 */
} bsp_gpio_config_t;

/**
  * @brief  GPIO 实例
  *
  * @note   由调用者分配（静态/全局/成员），驱动内部不 malloc。
  */
typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
    bsp_gpio_mode_t mode;
    uint8_t initialized;
} bsp_gpio_t;

/* Exported functions ------------------------------------------------------- */

/**
  * @brief  初始化一个 GPIO
  * @param  self   调用者提供的实例
  * @param  config 配置；不能为 NULL
  * @retval BSP_GPIO_OK          成功
  * @retval BSP_GPIO_ERR_PARAM   self/config/pin 非法
  * @retval BSP_GPIO_ERR_PORT    不支持的 GPIO 端口
  */
bsp_gpio_status_t bsp_gpio_init(bsp_gpio_t *self,
                                const bsp_gpio_config_t *config);

/**
  * @brief  反初始化，恢复为复位状态
  */
void bsp_gpio_deinit(bsp_gpio_t *self);

/**
  * @brief  写输出电平
  * @retval BSP_GPIO_OK        成功
  * @retval BSP_GPIO_ERR_PARAM self 为空
  * @retval BSP_GPIO_ERR_STATE 未初始化
  */
bsp_gpio_status_t bsp_gpio_write(bsp_gpio_t *self, bsp_gpio_level_t level);

/**
  * @brief  翻转输出电平
  */
bsp_gpio_status_t bsp_gpio_toggle(bsp_gpio_t *self);

/**
  * @brief  读取电平
  * @param  self  实例
  * @param  level 输出参数，不能为 NULL
  */
bsp_gpio_status_t bsp_gpio_read(const bsp_gpio_t *self,
                                bsp_gpio_level_t *level);

#ifdef __cplusplus
}
#endif

#endif /* BSP_GPIO_H */
