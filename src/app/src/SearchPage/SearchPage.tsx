import React, {useEffect} from 'react';
import axios from "axios";

import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import Grid from '@material-ui/core/Grid';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';

import TickerScoreList from "./TickerList";

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

export default function SearchPage () {
    const [filterList, setFilterList] = React.useState([]);
    const classes = useStyles();
    const gridSize = 3;

    const [isMounted, setIsMounted] = React.useState(false);
    const [tickerScoreList, setTickerScoreList ] = React.useState([]);
    const [chosenFilter, setChosenFilter] = React.useState("");
    const [queryMin, setQueryMin] = React.useState(0);
    const [queryMax, setQueryMax] = React.useState(100);

    useEffect( () => {
            if (!isMounted){
                setIsMounted(true)
                axios.get(`/filters`)
                    .then((res) => {
                        const filterList = res.data.filters;
                        setFilterList(filterList);
                        setChosenFilter(filterList[0]);
                    })
                setIsMounted(true);
                axios.get(`/ticker-scores`, {"params": {"short_list": "true"}})
                    .then((res) => {
                        setTickerScoreList(res.data.score_list);
                    })
            }
        },
        [isMounted]
    )

    const handleSelectFilter = (event: React.ChangeEvent<{ name?: string | undefined; value: unknown }>) => {
        const chosenFilter = event.target.value as string;
        setChosenFilter(chosenFilter);
    };

    const handleSearchBtn = () => {
        axios.post(`/ticker-scores`,
            {"filters": [
                    {name: chosenFilter, min: queryMin, max: queryMax}
                ]},
            {"params": {"short_list": "true"}},
        ).then((res) => {
            setTickerScoreList(res.data.score_list);
        })
    }

    return(
        <div>
            <Grid container justify="center" className={classes.root}>
                <Grid container justify="center">

                    <Grid item xs={gridSize}>
                        <FormControl className={classes.formControl}>
                            <TextField
                                label="Minimum"
                                type="number"
                                value={queryMin}
                                onChange={(event) =>
                                    setQueryMin(parseFloat(event.target.value))}
                                InputLabelProps={{ shrink: true }}
                                variant="outlined"
                            />
                        </FormControl>
                    </Grid>

                    <Grid item xs={gridSize}>
                        <FormControl className={classes.formControl}>
                            <InputLabel shrink>Algo Queries</InputLabel>
                            <Select
                                native
                                value={chosenFilter}
                                onChange={handleSelectFilter}
                                inputProps={{
                                    name: chosenFilter,
                                }}
                            >
                                {filterList.map(filter => <option key={filter} value={filter}>{filter}</option>)}
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid item xs={gridSize}>
                        <FormControl className={classes.formControl}>
                            <TextField
                                id="maximum"
                                label="Maximum"
                                type="number"
                                value={queryMax}
                                onChange={(event) =>
                                    setQueryMax(parseFloat(event.target.value))}
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                variant="outlined"
                            />
                        </FormControl>
                    </Grid>
                </Grid>
                <Grid item xs={12} justify="center">
                    <Button onClick={handleSearchBtn} variant="contained" color="primary">
                        Search
                    </Button>
                </Grid>
                <Grid justify="center">
                    <TickerScoreList filterList={filterList} tickerScoreList={tickerScoreList}/>
                </Grid>
            </Grid>

        </div>
    );
}

