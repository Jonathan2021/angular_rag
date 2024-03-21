import { createTheme } from "@mui/material";

export const theme = createTheme({
    typography: {
        h3: {
            fontFamily: "Roboto",
            fontSize: 18,
        },
        h4: {
            fontFamily: "Roboto",
            fontWeight: "bold",
            fontSize: 15,
        },
        h5: {
            fontFamily: "Roboto",
            fontWeight: "bold",
            fontSize: 14
        },
        body1: {
            fontFamily: "Roboto",
            fontSize: 14,
        },
        body2: {
            fontFamily: "Roboto",
            fontSize: 11,
        }
    },
});