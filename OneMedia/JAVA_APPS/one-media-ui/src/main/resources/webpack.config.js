const path = require('path');
// const UglifyJsPlugin = require('uglifyjs-webpack-plugin');


module.exports = {
    // mode: "development",
    mode: "production",
    context: path.resolve(__dirname),
    entry: {
        builderMenu: './static/site/js/sourceBundlerFile.js',
        adminMenu: './static/site/js/adminMenuBundler.js',
        queryPage: './static/site/js/queryPageBundler.js'
    },
    output: {
        filename: '[name]-bundled.js',
        path: path.resolve(__dirname, '../../../target/classes/static/site/dist')
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
        ],
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' для webpack 1
        },
    },
    // devtool: 'source-map'
};