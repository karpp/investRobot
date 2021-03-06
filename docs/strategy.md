# Модуль strategy

Содержит классы стратегии торгового робота.

## TradeStrategyBase

Интерфейс стратегии торгового робота. Содержит в себе логику обработки обновлений биржевых данных.
Пользователь может использовать одну из представленных реализаций
([RandomStrategy](#randomstrategy-), [MAEStrategy](#maestrategy-)) или реализовать собственную.

Торговый робот использует [bidirectional-stream](https://tinkoff.github.io/investAPI/head-marketdata/#bidirectional-stream)
Тинькофф Инвестиций для получения информации о событиях. Для настройки событий, на которые стратегии необходима подписка
следует использовать параметры стратегии `candle_subscription_interval`, `order_book_subscription_depth`, `trades_subscription`

Подробнее см. [примеры использования](#_2).

### Представленные реализации

#### `RandomStrategy` - Случайная стратегия
С каждым обновлением данных принимает решение о покупке / продаже рандомного числа лотов исходя из параметров, имеющихся
лотов и баланса. Не имеет потенциала, может использоваться для тестирования и в качестве примера стратегии.

#### `MAEStrategy` - Стратегия скользящего среднего
Данная стратегия основана на индикаторе скользящей средней.
Раз в минуту (при получении новой минутной свечи) рассчитывает два скользящих средних, длины которого можно задать
в конструкторе.
При изменении знака их разницы (пересечении линии скользящих средних) считает,
что текущий тренд цены изменился и отдает распоряжение на покупку / продажу, если "короткое" среднее выше или ниже
"длинного" соответственно. Покупает и продает каждый раз фиксированное число, изначально заданное в конструкторе,
при условии, что это возможно.


### Свойства

| Field                         | Type                                         | Description                          |
|-------------------------------|----------------------------------------------|--------------------------------------|
| candle_subscription_interval  | tinkoff.invest.SubscriptionInterval          | Период свечей для подписки           |
| order_book_subscription_depth | Optional[int]                                | Глубина стакана для подписки         |
| trades_subscription           | bool                                         | Подписка на обезличенные операции    |
| strategy_id                   | str                                          | id стратегии (используется логгером) |

### Методы

#### load_instrument_info
Запись информации об инструменте. Метод вызывается классом `TradeRobotFabric`.

*Входные данные*:

| Field           | Type                      | Description               |
|-----------------|---------------------------|---------------------------|
| instrument_info | tinkoff.invest.Instrument | Информация об инструменте |


#### load_candles
Загрузка исторических свечей. Вызывается роботом при начале торгов. Может быть переопределена пользователем для
настройки параметров стратегии.

*Входные данные*:

| Field   | Type                                | Description                |
|---------|-------------------------------------|----------------------------|
| candles | list[tinkoff.invest.HistoricCandle] | Список исторических свечей |

#### decide
Данный метод вызывается при получении новых биржевых данных. Возвращает объект, содержащий поручения торговому роботу.

*Входные данные*:

| Field       | Type                                        | Description              |
|-------------|---------------------------------------------|--------------------------|
| market_data | tinkoff.invest.MarketDataResponse           | Биржевые данные          |
| params      | [TradeStrategyParams](#tradestrategyparams) | Текущие параметры робота |

*Выходные данные*: [StrategyDecision](#strategydecision) - решения о действиях торгового робота.

#### decide_by_candle
Данный метод аналогичен методу decide, однако у него входные данные содержат только обновления свечей. Данный метод
необходим для бэктеста стратегии, так как получение исторических данных по стаканам и обезличенным операциям не
предоставляется возможным.

*Входные данные*:

| Field  | Type                                        | Description              |
|--------|---------------------------------------------|--------------------------|
| candle | tinkoff.invest.MarketDataResponse           | Свеча                    |
| params | [TradeStrategyParams](#tradestrategyparams) | Текущие параметры робота |

*Выходные данные*: [StrategyDecision](#strategydecision) - решения о действиях торгового робота.

## Структуры данных

### TradeStrategyParams
Структура данных, передаваемая на вход стратегии при обновлении данных.

| Field              | Type                            | Description                            |
|--------------------|---------------------------------|----------------------------------------|
| instrument_balance | int                             | Количество лотов инструмента на счету  |
| currency_balance   | float                           | Баланс счета                           |
| pending_orders     | list[tinkoff.invest.OrderState] | Список нереализованных биржевых заявок |

### RobotTradeOrder
Структура данных, содержащая получение торговому роботу на выставление рыночной заявки.

| Field      | Type                          | Description                                  |
|------------|-------------------------------|----------------------------------------------|
| quantity   | int                           | Количество лотов                             |
| direction  | tinkoff.invest.OrderDirection | Направление заявки (покупка / продажа)       |
| prive      | Optional[Money]               | Цена заявки (при отсутствии - рыночная цена) |
| order_type | tinkoff.invest.OrderType      | Тип заявки                                   |

### StrategyDecision
Структура данных, возвращаемая стратегией и содержащая решение о действиях торгового робота.

| Field             | Type                      | Description                                         |
|-------------------|---------------------------|-----------------------------------------------------|
| robot_trade_order | Optional[RobotTradeOrder] | Поручение роботу                                    |
| cancel_orders     | list[OrderState]          | Список биржевых заявок, которые необходимо отменить |
