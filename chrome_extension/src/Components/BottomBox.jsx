import React, { useState, useEffect } from 'react';
import './BottomBox.css';
import { Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto';
import { BeatLoader } from 'react-spinners';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
// yarn add react-transition-group 차트 슬라이드 효과
const BottomBox = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rankings, setRankings] = useState([]);
  const [bestKeyword, setBestKeyword] = useState(null);
  const [visibleLinks, setVisibleLinks] = useState({});
  const [keywordLinks, setKeywordLinks] = useState({});
  const [visibleChart, setVisibleChart] = useState(false);

  const handleClick = async () => {
    if (visibleChart) {
      setVisibleChart(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [recentWeekResponse, keywordRankingsResponse] = await Promise.all([
        fetch('http://localhost:8000/api/recent-week'),
        fetch('http://localhost:8000/api/keyword-rankings')
      ]);

      if (!recentWeekResponse.ok) {
        throw new Error('Failed to fetch recent week data');
      }
      if (!keywordRankingsResponse.ok) {
        throw new Error('Failed to fetch keyword rankings');
      }

      const recentWeekData = await recentWeekResponse.json();
      const keywordRankingsData = await keywordRankingsResponse.json();

      console.log('키워드 데이터 오는지 확인:', keywordRankingsData);
      console.log('날짜별 데이터 오는지 확인:', recentWeekData);

      const aggregatedData = aggregateData(recentWeekData);
      setData(aggregatedData);

      const bestRank = keywordRankingsData.rankings[0];
      setBestKeyword(bestRank);
      setRankings(keywordRankingsData.rankings);
      setVisibleChart(true);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePieChartClick = (elements) => {
    if (elements.length > 0) {
      const index = elements[0].index;
      const keyword = rankings[index].keyword;
      console.log('키워드 클릭됨:', keyword, rankings[index].links);

      setKeywordLinks({ [keyword]: rankings[index].links });
      setVisibleLinks({});
    }
  };

  const handleLineChartClick = (elements) => {
    if (elements.length > 0) {
      const index = elements[0].index;
      const date = data[index].date;
      console.log('날짜 클릭됨:', date, data[index].urls);

      setVisibleLinks({ [date]: true });
      setKeywordLinks({});
    }
  };

  const aggregateData = (data) => {
    const counts = data.reduce((acc, curr) => {
      const date = curr.date.split('T')[0];
      acc[date] = acc[date] || { count: 0, urls: [] };
      acc[date].count += 1;
      acc[date].urls.push({ link: curr.url, title: curr.title, type: curr.type, url: curr.url });
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
          label: '일주일 throw-wa 기록',
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

  const truncateLink = (text) => {
    const maxLength = 50;
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
  };

  return (
    <div className="bottom-box">
      <div className="button-container">
        <button onClick={handleClick} className="bottom-button">Throw Chart</button>
      </div>
      {loading && <div className="beat-loader-container"><BeatLoader color="#7289da" /></div>}
      {error && <p>Error: {error}</p>}
      <TransitionGroup>
        {visibleChart && rankings.length > 0 && (
          <CSSTransition key="rankings" timeout={300} classNames="chart">
            <div className="rankings">
              <h3>회원님의 가장 많이 저장한 카테고리는 <strong style={{ color: '#7289da' }}>{bestKeyword.keyword}</strong>입니다</h3>
              <Pie data={getPieChartData()} options={{ onClick: (e, elements) => handlePieChartClick(elements) }} />
            </div>
          </CSSTransition>
        )}
        {visibleChart && Object.keys(keywordLinks).map(keyword => (
          <CSSTransition key={keyword} timeout={300} classNames="keyword-links">
            <div className="keyword-links">
              <h3>{keyword} 링크</h3>
              <ul>
                {keywordLinks[keyword].map((link, index) => (
                  <li key={index}>
                    <span style={{ fontSize: 'larger' }}>
                      [{link.type}]
                    </span>
                    <a href={link.url} target="_blank" rel="noopener noreferrer" title={link.title} style={{ color: "#9bfe63" }}>
                      {truncateLink(link.title)}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </CSSTransition>
        ))}
        {visibleChart && data && (
          <CSSTransition key="chart" timeout={300} classNames="chart">
            <div className="chart-container">
              <Line data={getChartData()} options={{ onClick: (e, elements) => handleLineChartClick(elements) }} />
              <TransitionGroup>
                {Object.keys(visibleLinks).map(date => (
                  visibleLinks[date] && (
                    <CSSTransition key={date} timeout={300} classNames="bookmark-list">
                      <div className="bookmark-list">
                        <ul>
                          {data.find(item => item.date === date).urls.map((link, index) => (
                            <li key={index}>
                              <span style={{ fontSize: 'larger' }}>
                                [{link.type}]
                              </span>
                              <a href={link.url} target="_blank" rel="noopener noreferrer" title={link.title} style={{ color: "#9bfe63" }}>
                                {truncateLink(link.title)}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CSSTransition>
                  )
                ))}
              </TransitionGroup>
            </div>
          </CSSTransition>
        )}
      </TransitionGroup>
    </div>
  );
};

export default BottomBox;
