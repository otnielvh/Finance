import React from 'react';
import axios from 'axios';

export default class TickerScoreList extends React.Component {
  state = {
    ticker_score_list: [],
    filter_list: []
  }

  componentDidMount() {
    const ApiAxiosInstance = axios.create({
      baseURL: ''
    });
    ApiAxiosInstance.get(`/ticker-scores`, {"params": {"short_list": "true"}})
      .then((res) => {
        const tickers = res.data;
        const ticker_score_list = tickers.score_list;
        this.setState({ ticker_score_list });
      })

      ApiAxiosInstance.get(`/filters`)
      .then((res) => {
        const filter_list = res.data.filters;
        this.setState({ filter_list });
      })
  }

  render() {
    return (
      <table>
        <thead>
          <td>ticker</td>
          {this.state.filter_list.map(filter => <td>{filter}</td>)}
        </thead>
      
        { this.state.ticker_score_list.map((ticker_score) => {
          return <tr>
            <td> { ticker_score['ticker'] }</td>
            {this.state.filter_list.map(filter => <td>{ticker_score[filter]}</td>)}
          </tr>
          })
        }
      </table>
    )
  }
}