/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            colors: {
                white: "#fff",
                cornflowerblue: {
                    "100": "#2687d4",
                    "200": "#0060ae",
                    "300": "#004392",
                },
                gainsboro: {
                    "100": "#e6e6e6",
                    "200": "#dfdfdf",
                },
                gray: {
                    "100": "#fefefe",
                    "200": "#919191",
                    "300": "#8f8f8f",
                    "400": "#808080",
                    "500": "#181818",
                    "600": "rgba(0, 0, 0, 0.5)",
                },
                steelblue: {
                    "100": "#569ad0",
                    "200": "#5699d0",
                    "300": "#3d80b8",
                    "400": "#0094d4",
                },
                black: "#000",
                lightgray: "#cfcfcf",
                darkgray: "#aeaeae",
                deepskyblue: {
                    "100": "#3bb1e5",
                    "200": "#16aeec",
                },
                cadetblue: "#588b81",
                darkslategray: "rgba(51, 51, 51, 0.17)",
                dodgerblue: "#008dff",
                darkslateblue: "#005ba5",
            },
            spacing: {},
            fontFamily: {
                roboto: "Roboto",
                "pj-bold-18": "'Plus Jakarta Sans'",
                arial: "Arial",
                "hammersmith-one": "'Hammersmith One'",
                "pt-serif-caption": "'PT Serif Caption'",
                "pt-sans-caption": "'PT Sans Caption'",
                quicksand: "Quicksand",
                poppins: "Poppins",
                inter: "Inter",
                righteous: "Righteous",
            },
            borderRadius: {
                "10xs": "3px",
                "8xl": "27px",
                "11xl": "30px",
                "3xs": "10px",
                "81xl": "100px",
                "3xl": "22px",
                "31xl": "50px",
                "6xl": "25px",
                "10xl": "29px",
                "34xl": "53px",
            },
            height: {
                'screen-mobile': '100%',
                'screen-desktop': '100vh',
            },
        },
        fontSize: {
            xs: "12px",
            base: "16px",
            mini: "15px",
            "3xl": "22px",
            lg: "18px",
            "8xl": "27px",
            xl: "20px",
            "2xs": "11px",
            "5xl": "24px",
            lgi: "19px",
            sm: "14px",
            inherit: "inherit",
            "29xl": "48px",
            "10xl": "29px",
            "77xl": "96px",
            "19xl": "38px",
            "13xl": "32px",
            "7xl": "26px",
            "33xl": "52px",
            "12xl": "31px",
            "23xl": "42px",
        },
        screens: {
            '2xs': '375px',
            '3xs': '425px',
            sm: '640px',
            md: '768px',
            lg: '1024px',
            xl: '1280px',
            '2xl': '1536px',
            mq1350: { raw: "screen and (max-width: 1350px)" },
            lg: { max: "1200px" },
            mq1150: { raw: "screen and (max-width: 1150px)" },
            mq1125: { raw: "screen and (max-width: 1125px)" },
            mq1050: { raw: "screen and (max-width: 1050px)" },
            mq1025: { raw: "screen and (max-width: 1025px)" },
            mq900: { raw: "screen and (max-width: 900px)" },
            mq800: { raw: "screen and (max-width: 800px)" },
            mq750: { raw: "screen and (max-width: 750px)" },
            mq675: { raw: "screen and (max-width: 675px)" },
            mq540: { raw: "screen and (max-width: 540px)" },
            mq450: { raw: "screen and (max-width: 450px)" },
            mq1325: {
                raw: "screen and (max-width: 1325px)",
            },
            mq350: {
                raw: "screen and (max-width: 350px)",
            },
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
