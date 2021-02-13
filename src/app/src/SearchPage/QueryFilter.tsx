import React, {useEffect} from 'react';
import Grid from "@material-ui/core/Grid";
import FormControl from "@material-ui/core/FormControl";
import TextField from "@material-ui/core/TextField";
import InputLabel from "@material-ui/core/InputLabel";
import Select from "@material-ui/core/Select";
import {createStyles, makeStyles, Theme} from "@material-ui/core/styles";

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        formControl: {
            margin: theme.spacing(1),
            minWidth: 120,
        },
        root: {
            flexGrow: 1,
        },
    }),
);

export default function QueryFilter (props: any) {
    const classes = useStyles();
    const gridSize = 2;
    const index = props.index;
    return (
        <Grid container justify="center">
            <Grid item xs={gridSize}>
                <FormControl className={classes.formControl}>
                    <TextField
                        label="Minimum"
                        type="number"
                        value={props.queryMin}
                        onChange={(event) =>
                            props.setQueryMin(index, parseFloat(event.target.value))}
                        InputLabelProps={{shrink: true}}
                        variant="outlined"
                    />
                </FormControl>
            </Grid>

            <Grid item xs={gridSize}>
                <FormControl className={classes.formControl}>
                    <InputLabel shrink>Algo Queries</InputLabel>
                    <Select
                        native
                        value={props.chosenFilter}
                        onChange={(event) =>
                            props.handleSelectFilter(props.index, event)
                        }
                        inputProps={{
                            name: props.chosenFilter,
                        }}
                    >
                        {props.filterList.map((filter: string) => <option key={filter} value={filter}>{filter}</option>)}
                    </Select>
                </FormControl>
            </Grid>

            <Grid item xs={gridSize}>
                <FormControl className={classes.formControl}>
                    <TextField
                        id="maximum"
                        label="Maximum"
                        type="number"
                        value={props.queryMax}
                        onChange={(event) =>
                            props.setQueryMax(index, parseFloat(event.target.value))}
                        InputLabelProps={{
                            shrink: true,
                        }}
                        variant="outlined"
                    />
                </FormControl>
            </Grid>
        </Grid>
    )
}