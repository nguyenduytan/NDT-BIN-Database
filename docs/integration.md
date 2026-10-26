# Integration

Use `data/bins.json` for a small application or `data/bins.sqlite` for server-side
lookup. Keep `bin` as a string in JavaScript and Python so values such as `004078`
retain their leading zeroes.

```js
const bins = await fetch("./data/bins.json").then((response) => response.json());
const match = bins.find((item) => item.bin === "004078");
```

For a service, run `uvicorn ndt_bin.api:app` and query `/api/v1/bins`. Filter
parameters can be combined. Page size is capped at 200.
