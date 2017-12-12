const express = require("express");
const app = express();

const PORT = 8080;


let currentIP = '';

/* GET PI GLOVE DATA */
app.get('/glove', (req, res) => {
  res.send(currentIP);
});

/* SET PI GLOVE DATA */
app.post('/glove', (req, res) => {
  console.log(req.query);
  if (req.query.newIP) {
    currentIP = req.query.newIP;
    res.status(200).send('success');
  } else {
    res.send('failed');
  }
});

app.listen(PORT, () => {
 console.log('Listening on port '+ PORT);
});