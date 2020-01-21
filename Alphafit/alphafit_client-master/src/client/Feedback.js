import React, { Component } from 'react';

class Feedback extends Component {
  static defaultProps = {
    feedback: {
        reps: 0,
        majorProblems: ['분석되지 않았습니다'],
        minorProblems: ['분석되지 않았습니다'],
        strengths: ['분석되지 않았습니다']
    }
  }

  translator = (problem) => {
    switch(problem) {
      case "stance_width":
        return "보폭 넓이";
      case "bend_hips_knees":
        return "고관절과 무릎 접히는 타이밍";
      case "squat_depth":
        return "스쿼트 깊이"
      case "knees_over_toes":
        return "무릎 돌출 정도"
      case "back_hip_angle":
        return "상체 각도"
    } 
  };

  mapAdvice = (problem) => {
    switch(problem) {
      case "stance_width":
        return "보폭이 올바르지 않습니다. 발을 어깨 넓이로 벌려주세요";
      case "bend_hips_knees":
        return "고관절과 무릎이 동시에 접히도록 해 주세요";
      case "squat_depth":
        return "스쿼트 깊이가 부족합니다. 조금 더 내려가 주세요"
      case "knees_over_toes":
        return "발끝 밖으로 무릎이 나가는 경향이 있습니다, 신경 써 주세요"
      case "back_hip_angle":
        return "상체 각도에 문제가 있습니다. 상체 각을 적절하게 유지하여 주세요"
    }  
  };

  mapGood = (problem) => {
    switch(problem) {
      case "stance_width":
        return "스탠스가 좋습니다. 현재 보폭을 유지해 주세요";
      case "bend_hips_knees":
        return "고관절과 무릎이 접히는 타이밍이 완벽합니다";
      case "squat_depth":
        return "스쿼트 깊이가 적절합니다"
      case "knees_over_toes":
        return "무릎이 과하게 돌출되지 않아 적절합니다"
      case "back_hip_angle":
        return "상체 각도에 문제가 없습니다"
    }  
  };

  render() {

    const majorElems = this.props.feedback.majorProblems.map((item, key) =>
      <li key={key}>{this.translator(item)}</li>
    );

    const minorElems = this.props.feedback.minorProblems.map((item, key) =>
      <li key={key}>{this.translator(item)}</li>
    );

    const strengthElems = this.props.feedback.strengths.map((item, key) =>
      <li key={key}>{this.translator(item)}</li>
    );    

    const majorAdvice = this.props.feedback.majorProblems.map((item, key) =>
      <li key={key}>{this.mapAdvice(item)}</li>
    );

    const minorAdvice = this.props.feedback.minorProblems.map((item, key) =>
      <li key={key}>{this.mapAdvice(item)}</li>
    );

    const strengthGood = this.props.feedback.strengths.map((item, key) =>
      <li key={key}>{this.mapGood(item)}</li>
    );

    const style = {
      padding: '8px',
      margin: '8px'
    };
  
    return (
      <div style={style}>
        <div className="repAnalyzed">총 <b>{this.props.feedback.reps}</b>개의 스쿼트 동작이 분석되었습니다</div>
        <br/>
        <div className="row">
          <div className="col s4">
            <div className="subHeader">Major Problems</div>
            <ul>
              {majorElems}
            </ul>
          </div>
          <div className="col s4">
            <div className="subHeader">Minor Problems</div>
            <ul>
              {minorElems}
            </ul>
          </div>
          <div className="col s4">
            <div className="subHeader goldFont">Strengths</div>
            <ul>
              {strengthElems}
            </ul>
          </div>
        </div>
        <div>
          <div className="subHeader">Negative Feedback</div> 
          <ul>
            {majorAdvice}
            {minorAdvice}
          </ul>         
          <div className="subHeader">Positive Feedback</div> 
          <ul>
            {strengthGood}
          </ul>
        </div>
      </div>
    );
  }
}

export default Feedback;