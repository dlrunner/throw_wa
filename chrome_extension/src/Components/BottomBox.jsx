import React, { useState, useEffect } from 'react';
import './BottomBox.css';
import { Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto'; // yarn add chart.js  //  yarn add react-chartjs-2 설치해야됨

const BottomBox = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rankings, setRankings] = useState([]);

  const handleClick = async (buttonNumber) => {
    if (buttonNumber === 1) {
      setLoading(true);
      setError(null);
      setRankings([]);
      try {
        const response = await fetch('http://localhost:8000/api/recent-week');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const result = await response.json();
        const aggregatedData = aggregateData(result);
        setData(aggregatedData);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    } else if (buttonNumber === 2) {
      setLoading(true);
      setError(null);
      setData(null);
      try {
        const response = await fetch('http://localhost:8000/api/keyword-rankings');
        if (!response.ok) {
          throw new Error('Failed to fetch keyword rankings');
        }
        const result = await response.json();
        setRankings(result.rankings);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    } else {
      alert(`Button ${buttonNumber} clicked!`);
    }
  };

  const aggregateData = (data) => {
    const counts = data.reduce((acc, curr) => {
      const date = curr.date.split('T')[0];
      acc[date] = acc[date] || { count: 0, urls: [] };
      acc[date].count += 1;
      acc[date].urls.push(curr.url);
      return acc;
    }, {});

    return Object.keys(counts).map(date => ({ date, count: counts[date].count, urls: counts[date].urls }));
  };

  const getChartData = () => {
    if (!data) return null;
    const labels = data.map(item => item.date);
    const values = data.map(item => item.count);
    return {
      labels,
      datasets: [
        {
          label: '일주일간 북마크 기록',
          data: values,
          fill: false,
          backgroundColor: 'rgba(75,192,192,0.6)',
          borderColor: 'rgba(75,192,192,1)',
        },
      ],
    };
  };

  const getPieChartData = () => {
    if (rankings.length === 0) return null;
    const labels = rankings.map(rank => rank.keyword);
    const values = rankings.map(rank => rank.count);
    return {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
            '#FF9F40'
          ],
          hoverBackgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
            '#FF9F40'
          ]
        }
      ]
    };
  };

  const truncateLink = (url) => {
    const maxLength = 50;
    if (url.length <= maxLength) return url;
    return `${url.substring(0, maxLength)}...`;
  };

  return (
    <div className="bottom-box">
      <div className="button-container">
        <button onClick={() => handleClick(1)} className="bottom-button">history</button>
        <button onClick={() => handleClick(2)} className="bottom-button">Button 2</button>
        <button onClick={() => handleClick(3)} className="bottom-button">Button 3</button>
      </div>
      {loading && <div className="loading-bar"></div>}
      {error && <p>Error: {error}</p>}
      {data && (
        <div className="chart-container">
          <Line data={getChartData()} />
          <div className="bookmark-list">
            {data.map(item => (
              <div key={item.date}>
                <h3>{item.date}</h3>
                <ul>
                  {item.urls.map((url, index) => (
                    <li key={index}><a href={url} target="_blank" rel="noopener noreferrer">{truncateLink(url)}</a></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
      {rankings.length > 0 && (
        <div className="rankings">
          <h3>키워드 랭킹</h3>
          <Pie data={getPieChartData()} />
        </div>
      )}
    </div>
  );
};

export default BottomBox;
