module.exports = {
  '*.{js,mjs,cjs,ts,mts,cts,vue,json}': ['prettier --write'],
  '*.{js,mjs,cjs,ts,mts,cts,vue}': ['eslint --fix'],
};
