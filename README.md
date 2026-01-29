# Unit system

Website for the management of a warehouse system.
The goal of this project is to learn the Flask framework and
containarization using docker.

## How to run

Clone the repository with:

```bash
git clone https://github.com/dimitriszitonoulis/warehouse_system.git
```

### With docker

Install the docker engine.
Move into the `warehouse_system` directory and run

```bash
docker compose up -d
```


### Login

Open a browser and visit `http://localhost:5000`

#### As employee

| Field | Value |
| --- | --- |
| username | js |
| password | 12 |
| unit id | u1 |

#### As supervisor

| Field | Value |
| --- | --- |
| username | bw |
| password | 12 |
| unit id | u1 |


## MongoDB collections

### user

|Field|Type|
|--|--|
|id|string|
|name|string|
|surname|string|
|username|string|
|password|string|
|unit_id|string|
|role|string (takes values employee, supervisor, admin)|

### Unit

|Field|Type|
|--|--|
|id|string|
|name|string|
|volume|float|

### Employees and Supervisors

|Field|Type|
|--|--|
|id|string|
|name|string|
|surname|string|
|username|string|
|password|string|
|unit_id|string|

### Products

|Field|Type|
|--|--|
|id|string|
|name|string|
|quantity|int|
|sold_quantity|int|
|weight|float|
|volume|float|
|category|string|
|purchase_price|float|
|selling_price|float|
|manufacturer|string|
|unit_gain|float|
|unit_id|string|

unit_id is not attribute of Product class but it needs to be stored with the product
