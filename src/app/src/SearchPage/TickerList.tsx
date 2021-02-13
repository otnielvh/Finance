import React from 'react';

export default function TickerScoreList(props: any) {

    return (
        <table>
            <thead>
            <tr>
                <td>ticker</td>
                {props.filterList.map((filter: string) => <td key={filter}>{filter}</td>)}
            </tr>
            </thead>
            <tbody>
            { props.tickerScoreList.map((tickerScore: any) => {
                    return <tr>
                        <td key={tickerScore['ticker']}> { tickerScore['ticker'] }</td>
                        {props.filterList.map((filter: string) => <td key={filter}>{tickerScore[filter]}</td>)}
                    </tr>
                }
            )}
            </tbody>
        </table>
    )
}
