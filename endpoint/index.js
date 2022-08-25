const cors = require('cors');
const express = require('express');
const app = express();
const port = process.env.USED_PORT || 3001;

app.use(cors());
app.set('json spaces', 2);

app.get('/', async (req, res) => {
  const data = require('../output/output.json');
  if (data) {
    res.json(data);
  } else {
    res.status(404);
    res.end();
  }
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
