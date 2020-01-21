import React, { Component } from 'react';
import './app.css';
import { Button } from 'react-materialize';
import "materialize-css/dist/css/materialize.min.css";
import io from 'socket.io-client'
import Feedback from './Feedback'
const serverAddress = "http://localhost:3000"

export default class App extends Component {

  constructor(props) {
    super(props);
    this.display = React.createRef();
    this.socket = null,
    this.state = {
      colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff', '#ff00ff'],
      HANDSIZE: 20,
      HANDCLOSEDCOLOR: "red",
      HANDOPENCOLOR:"green",
      HANDLASSOCOLOR: "blue",
      resultData: {
        reps: 0,
        majorProblems: ['분석되지 않았습니다'],
        minorProblems: ['분석되지 않았습니다'],
        strengths: ['분석되지 않았습니다']
      },
      recordState: 0,
    }
  }

  updateHandState(handState, jointPoint) {
    switch (handState) {
      case 3:
        this.drawHand(jointPoint, this.state.HANDCLOSEDCOLOR);
      break;
      case 2:
        this.drawHand(jointPoint, this.state.HANDOPENCOLOR);
      break;
      case 4:
        this.drawHand(jointPoint, this.state.HANDLASSOCOLOR);
      break;
    }
  }

  drawHand(jointPoint, handColor) {
    // draw semi transparent hand cicles
    let ctx = this.display.current.getContext('2d');
    ctx.globalAlpha = 0.75;
    ctx.beginPath();
    ctx.fillStyle = handColor;
    ctx.arc(jointPoint.depthX * 512, jointPoint.depthY * 424, this.stateHANDSIZE, 0, Math.PI * 2, true);
    ctx.fill();
    ctx.closePath();
    ctx.globalAlpha = 1;
  }

  componentDidMount() {
    console.log("react ready to go through")
    let self = this

    self.socket = io(serverAddress);

    self.socket.on('bodyFrame', bodyFrame => {
      let ctx = self.display.current.getContext('2d');
      ctx.clearRect(0, 0, self.display.current.width, self.display.current.height);
      let index = 0;
      let colors = self.state.colors;

      bodyFrame.bodies.forEach(function(body){
        if(body.tracked) {
          for(let jointType in body.joints) {
            let joint = body.joints[jointType];
            ctx.fillStyle = colors[index];
            ctx.fillRect(joint.depthX * 512, joint.depthY * 424, 10, 10);
          }
          //draw hand states
          self.updateHandState(body.leftHandState, body.joints[7]);
          self.updateHandState(body.rightHandState, body.joints[11]);
          index++;
        }
      });

    });
  };

  clickRecordButton = () => {
    self = this;
    self.setState({recordState: 1});
    setTimeout(function(){
      self.setState({recordState: 2})
    }, 20000);

    fetch('/api/startRecord')
    .then((response) => { return response.json(); })
    .then((data) => {
      const items = data;
      if (items["success"] == 1) {
        self.setState({
          resultData: {
            reps: items["reps"],
            majorProblems: items["majorProblems"],
            minorProblems: items["minorProblems"],
            strengths: items["strengths"]          
          },
          recordState: 3
        });
      } else {
        self.setState({
          resultData: {
            reps: 0,
            majorProblems: ["분석 실패"],
            minorProblems: ["분석 실패"],
            strengths: ["분석 실패"]         
          },
          recordState: 3
        });
      }
    });
  }

  render() {
    let recordBtn, content;
    if (this.state.recordState === 0) {
      recordBtn = <Button className="waves-effect waves-light btn recordBtn red" onClick={this.clickRecordButton}>
                    <i className="material-icons left">fiber_manual_record</i>
                    Start Record
                  </Button>
      content = <div className="readtSpace">
                  <p className="evalText">
                    녹화 버튼을 누르면 즉시 녹화가 시작됩니다.
                  </p>
                  <p className="evalText">
                    녹화가 끝날 때까지, 20초간 스쿼트 동작을 반복해 주세요
                  </p>
                  <p className="evalTextSm">
                    동작이나, 카메라와의 거리에 따라 계측이 되지 않을 수 있습니다
                  </p>
                </div>
    } else if (this.state.recordState === 1) {
      recordBtn = null
      content = <div className="loaderSpace">
                <div class="spinner">
                  <div class="double-bounce1"></div>
                  <div class="double-bounce2"></div>
                </div>
                  <p className="evalText">
                    동작을 녹화하는 중입니다.<br/>
                    스쿼트를 계속 수행해 주세요
                  </p>
                </div>
    } else if (this.state.recordState === 2) {
      recordBtn = null
      content = <div className="loaderSpace">
                  <div class="loader">Loading...</div>
                  <p className="evalText">
                    녹화된 모션 데이터를 평가하고 있습니다
                  </p>
                </div>
    } else {
      recordBtn = <Button className="waves-effect waves-light btn recordBtn red" onClick={this.clickRecordButton}>
                    <i className="material-icons left">fiber_manual_record</i>
                    Start Record
                  </Button>
      content = <div className="feedbackSpace">
                  <Feedback feedback={this.state.resultData}/>
                </div>      
    }

    return (
      <React.Fragment>
        <div className="app-container">
          <div className="row" style={{ marginTop:'15vh'}}>
            <div className="col s6">
              <div className="center-align">
                <canvas className="display" width="512" height="424" ref={this.display}></canvas>
                <div>
                  {recordBtn}
                </div>
              </div>  
            </div>
            <div className="col s6">
              <div className="card black darken-1 feedbackCard">
                <div className="card-content white-text">
                  <span className="card-title">AI FeedBack</span>
                  <br/>
                  {content}
                </div>
              </div>
            </div>               
          </div>
        </div>
      </React.Fragment>
    );
  }
}
