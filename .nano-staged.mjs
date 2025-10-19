import {resolve} from 'path';

export default {
  // Lint only staged files under webapp
  'webapp/**/*.{js,mjs,cjs,ts,mts,cts,vue}': ({filenames}) => {
    const files = filenames.map(f => resolve('.', f)).join(' ');
    return files ? [`npx --prefix webapp eslint --cache --fix ${files}`] : [];
  },
};
