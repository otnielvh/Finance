import React, {useEffect} from 'react';
import axios from "axios";

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Fab from '@material-ui/core/Fab';
import AddIcon from '@material-ui/icons/Add';


import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';

import TickerScoreList from "./TickerList";
import QueryFilter from "./QueryFilter";

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        formControl: {
            margin: theme.spacing(1),
            minWidth: 120,
        },
        root: {
            flexGrow: 1,
        },
        margin: {
            margin: theme.spacing(1),
        },
    }),
);

export default function SearchPage () {
    const classes = useStyles();


    const [filterList, setFilterList] = React.useState([]);
    const [isMounted, setIsMounted] = React.useState(false);
    const [tickerScoreList, setTickerScoreList ] = React.useState([]);

    const [queryCount, setQueryCount] = React.useState(1);
    const [chosenFilter, setChosenFilter] = React.useState([""]);
    const [queryMin, setQueryMin] = React.useState([0]);
    const [queryMax, setQueryMax] = React.useState([100]);

    const setIndexedChosenFilter = (index: number, value: string) => {
        const myChosenFilter = [...chosenFilter];
        myChosenFilter[index] = value;
        setChosenFilter(myChosenFilter);
    }

    const setIndexedQueryMax = (index: number, value: number) => {
        const myQueryMax = [...queryMax];
        myQueryMax[index] = value;
        setQueryMax(myQueryMax);
    }

    const setIndexedQueryMin = (index: number, value: number) => {
        const myQueryMin = [...queryMin];
        myQueryMin[index] = value;
        setQueryMin(myQueryMin);
    }

    useEffect( () => {
            if (!isMounted){
                setIsMounted(true)
                axios.get(`/filters`)
                    .then((res) => {
                        const filterList = res.data.filters;
                        setFilterList(filterList);
                        setChosenFilter([filterList[0]]);
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

    const handleIndexedChosenFilter = (index: number, event: React.ChangeEvent<{ name?: string | undefined; value: unknown }>) => {
        const chosenFilter = event.target.value as string;
        setIndexedChosenFilter(index, chosenFilter);
    };

    const handleSearchBtn = () => {
        let _filterList = []
        for (let i=0; i < queryCount; i++) {
            _filterList.push({
                name: chosenFilter[i],
                min: queryMin[i],
                max: queryMax[i],
            })
        }
        axios.post(`/ticker-scores`,
            {"filters": _filterList},
            {"params": {"short_list": "true"}},
        ).then((res) => {
            setTickerScoreList(res.data.score_list);
        })
    }


    const queryFilterList = []
    for (let i = 0; i < queryCount; i++) {
        queryFilterList.push(
            <QueryFilter
                index={i}
                chosenFilter={chosenFilter[i]}
                handleSelectFilter={handleIndexedChosenFilter}
                filterList={filterList}
                queryMax={queryMax[i]}
                setQueryMin={setIndexedQueryMin}
                queryMin={queryMin[i]}
                setQueryMax={setIndexedQueryMax}
            />
        )
    }

    return(
        <div>
            <Grid container justify="center" className={classes.root}>
                <Grid container>
                    {queryFilterList}
                </Grid>


                <Grid item xs={3} justify="flex-start">
                    <Button onClick={handleSearchBtn} variant="contained" color="primary">
                        Search
                    </Button>
                </Grid>
                <Grid item xs={3} justify="flex-end">
                    <Fab size="small" color="primary" aria-label="add" className={classes.margin}>
                        <AddIcon onClick={() => {
                            setChosenFilter([...chosenFilter, filterList[0]])
                            setQueryMax([...queryMax, 100])
                            setQueryMin([...queryMin, 0])
                            setQueryCount(queryCount + 1)
                        }}/>
                    </Fab>
                </Grid>

                <Grid justify="center">
                    <TickerScoreList filterList={filterList} tickerScoreList={tickerScoreList}/>
                </Grid>

            </Grid>

        </div>
    );
}

