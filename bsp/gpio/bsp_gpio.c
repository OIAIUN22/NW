/**
  ******************************************************************************
  * @file    bsp_gpio.c
  * @brief   STM32F1 GPIO 纯驱动实现
  *
  * 设计要点：
  *   1. 只做 GPIO 的 init/deinit/read/write/toggle；
  *   2. 不出现 LED、按键、业务状态机；
  *   3. 不使用动态内存、FreeRTOS、HAL_Delay；
  *   4. 端口时钟由驱动按 port 自动使能，避免“忘了开时钟”；
  *   5. 所有可能失败的接口返回 bsp_gpio_status_t。
  ******************************************************************************
  */

#include "gpio/bsp_gpio.h"

#include <stddef.h>

/* Private functions ---------------------------------------------------------*/

static bsp_gpio_status_t bsp_gpio_enable_clock(GPIO_TypeDef *port)
{
    if (port == GPIOA) {
        __HAL_RCC_GPIOA_CLK_ENABLE();
        return BSP_GPIO_OK;
    }
    if (port == GPIOB) {
        __HAL_RCC_GPIOB_CLK_ENABLE();
        return BSP_GPIO_OK;
    }
    if (port == GPIOC) {
        __HAL_RCC_GPIOC_CLK_ENABLE();
        return BSP_GPIO_OK;
    }
    if (port == GPIOD) {
        __HAL_RCC_GPIOD_CLK_ENABLE();
        return BSP_GPIO_OK;
    }
#ifdef GPIOE
    if (port == GPIOE) {
        __HAL_RCC_GPIOE_CLK_ENABLE();
        return BSP_GPIO_OK;
    }
#endif
    return BSP_GPIO_ERR_PORT;
}

static uint32_t bsp_gpio_hal_mode(bsp_gpio_mode_t mode)
{
    switch (mode) {
    case BSP_GPIO_MODE_INPUT:      return GPIO_MODE_INPUT;
    case BSP_GPIO_MODE_OUTPUT_PP: return GPIO_MODE_OUTPUT_PP;
    case BSP_GPIO_MODE_OUTPUT_OD: return GPIO_MODE_OUTPUT_OD;
    case BSP_GPIO_MODE_ANALOG:    return GPIO_MODE_ANALOG;
    default:                      return 0xFFFFFFFFu;
    }
}

static uint32_t bsp_gpio_hal_pull(bsp_gpio_pull_t pull)
{
    switch (pull) {
    case BSP_GPIO_PULL_NONE: return GPIO_NOPULL;
    case BSP_GPIO_PULL_UP:   return GPIO_PULLUP;
    case BSP_GPIO_PULL_DOWN: return GPIO_PULLDOWN;
    default:                 return 0xFFFFFFFFu;
    }
}

static uint32_t bsp_gpio_hal_speed(bsp_gpio_speed_t speed)
{
    switch (speed) {
    case BSP_GPIO_SPEED_LOW:    return GPIO_SPEED_FREQ_LOW;
    case BSP_GPIO_SPEED_MEDIUM: return GPIO_SPEED_FREQ_MEDIUM;
    case BSP_GPIO_SPEED_HIGH:   return GPIO_SPEED_FREQ_HIGH;
    default:                    return 0xFFFFFFFFu;
    }
}

/* Exported functions -------------------------------------------------------*/

bsp_gpio_status_t bsp_gpio_init(bsp_gpio_t *self,
                                const bsp_gpio_config_t *config)
{
    if (self == NULL || config == NULL) {
        return BSP_GPIO_ERR_PARAM;
    }
    if (config->port == NULL || config->pin == 0u) {
        return BSP_GPIO_ERR_PARAM;
    }

    const uint32_t hal_mode = bsp_gpio_hal_mode(config->mode);
    const uint32_t hal_pull = bsp_gpio_hal_pull(config->pull);
    const uint32_t hal_speed = bsp_gpio_hal_speed(config->speed);
    if (hal_mode == 0xFFFFFFFFu ||
        hal_pull == 0xFFFFFFFFu ||
        hal_speed == 0xFFFFFFFFu) {
        return BSP_GPIO_ERR_PARAM;
    }

    bsp_gpio_status_t status = bsp_gpio_enable_clock(config->port);
    if (status != BSP_GPIO_OK) {
        return status;
    }

    /* 输出模式先写初始电平，再配置为输出，避免上电毛刺。 */
    if (config->mode == BSP_GPIO_MODE_OUTPUT_PP ||
        config->mode == BSP_GPIO_MODE_OUTPUT_OD) {
        HAL_GPIO_WritePin(config->port, config->pin,
                          (config->initial == BSP_GPIO_HIGH)
                              ? GPIO_PIN_SET
                              : GPIO_PIN_RESET);
    }

    GPIO_InitTypeDef init = {0};
    init.Pin = config->pin;
    init.Mode = hal_mode;
    init.Pull = hal_pull;
    init.Speed = hal_speed;
    HAL_GPIO_Init(config->port, &init);

    self->port = config->port;
    self->pin = config->pin;
    self->mode = config->mode;
    self->initialized = 1u;

    return BSP_GPIO_OK;
}

void bsp_gpio_deinit(bsp_gpio_t *self)
{
    if (self == NULL) {
        return;
    }
    if (self->initialized != 0u && self->port != NULL) {
        HAL_GPIO_DeInit(self->port, self->pin);
    }

    self->port = NULL;
    self->pin = 0u;
    self->mode = BSP_GPIO_MODE_INPUT;
    self->initialized = 0u;
}

bsp_gpio_status_t bsp_gpio_write(bsp_gpio_t *self, bsp_gpio_level_t level)
{
    if (self == NULL) {
        return BSP_GPIO_ERR_PARAM;
    }
    if (self->initialized == 0u) {
        return BSP_GPIO_ERR_STATE;
    }
    if (self->mode == BSP_GPIO_MODE_INPUT ||
        self->mode == BSP_GPIO_MODE_ANALOG) {
        return BSP_GPIO_ERR_STATE;
    }
    if (level != BSP_GPIO_LOW && level != BSP_GPIO_HIGH) {
        return BSP_GPIO_ERR_PARAM;
    }

    HAL_GPIO_WritePin(self->port, self->pin,
                      (level == BSP_GPIO_HIGH) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    return BSP_GPIO_OK;
}

bsp_gpio_status_t bsp_gpio_toggle(bsp_gpio_t *self)
{
    if (self == NULL) {
        return BSP_GPIO_ERR_PARAM;
    }
    if (self->initialized == 0u) {
        return BSP_GPIO_ERR_STATE;
    }
    if (self->mode == BSP_GPIO_MODE_INPUT ||
        self->mode == BSP_GPIO_MODE_ANALOG) {
        return BSP_GPIO_ERR_STATE;
    }

    HAL_GPIO_TogglePin(self->port, self->pin);
    return BSP_GPIO_OK;
}

bsp_gpio_status_t bsp_gpio_read(const bsp_gpio_t *self,
                                bsp_gpio_level_t *level)
{
    if (self == NULL || level == NULL) {
        return BSP_GPIO_ERR_PARAM;
    }
    if (self->initialized == 0u) {
        return BSP_GPIO_ERR_STATE;
    }

    const GPIO_PinState state = HAL_GPIO_ReadPin(self->port, self->pin);
    *level = (state == GPIO_PIN_SET) ? BSP_GPIO_HIGH : BSP_GPIO_LOW;
    return BSP_GPIO_OK;
}
