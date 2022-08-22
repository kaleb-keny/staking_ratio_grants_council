module.exports = [
  {
    script: 'index.js',
    name: 'endpoint',
    instances: 'max',
    exec_mode: 'cluster',
  },
];
