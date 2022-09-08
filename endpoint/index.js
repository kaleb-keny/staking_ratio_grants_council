const fs = require('fs/promises');
const cors = require('cors');
const express = require('express');
const app = express();
const port = process.env.USED_PORT || 3001;

app.use(cors());
app.set('json spaces', 2);

app.get('/', async (req, res) => {
  const rawData = await fs.readFile(`${__dirname}/output/output.json`);
  const parsedData = JSON.parse(rawData);
  if (parsedData) {
    res.json(parsedData);
  } else {
    res.status(404);
    res.end();
  }
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
