import React, { Component } from "react";
import ModelViewer from '@metamask/logo';  // yarn add @metamask/logo 설치하셈

class MetamaskLogo extends Component {
  componentDidMount() {
    this.viewer = ModelViewer({
      pxNotRatio: true,
      width: 120,
      height: 120,
      followMouse: true
    });
    this.el.appendChild(this.viewer.container);
  }

  componentWillUnmount() {
    if (this.viewer) {
      this.viewer.stopAnimation();
    }
  }

  render() {
    return (
      <div
        // style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
        ref={el => (this.el = el)}
      />
    );
  }
}

export default MetamaskLogo;
