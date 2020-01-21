const express = require('express');
const os = require('os');
const app = express();
const Kinect2 = require('kinect2');
const kinect = new Kinect2();
const axios = require('axios')

const server = app.listen(process.env.PORT || 3000, () => console.log(`Listening on port ${process.env.PORT || 3000}!`));
const io = require('socket.io').listen(server);

app.use(express.static('dist'));

app.get('/', function(req, res) {
    res.sendFile(__dirname + '/public/index.html');
});

function sleep(delay) {
    var start = new Date().getTime();
    while (new Date().getTime() < start + delay);
}

if(kinect.open()) {
    console.log("kinect ready to operate");

    // 클라이언트 소켓으로 녹화된 bodyFrame 송신 
    kinect.on('bodyFrame', function(bodyFrame){
        io.sockets.emit('bodyFrame', bodyFrame);      
    });
    
    // 동작 녹화 시작
    app.get('/api/startRecord', (req, res) =>  {
        console.log("start record");
        let recordData = ""
        kinect.on('bodyFrame', function(bodyFrame){
            for(var i = 0;  i < bodyFrame.bodies.length; i++) {
                if(bodyFrame.bodies[i].tracked) {
                    for(var j = 0;  j < bodyFrame.bodies[i].joints.length; j++) {
                        recordData += bodyFrame.bodies[i].joints[j]["depthX"] * 512
                        recordData += ","
                        recordData += bodyFrame.bodies[i].joints[j]["depthY"] * 424
                        recordData += ","
                        recordData += bodyFrame.bodies[i].joints[j]["cameraZ"]
                        recordData += ","
                    }	
                    recordData = recordData.substring(0, recordData.length - 1);	
                    recordData += "\n"
                }
            } 
        });  

        // 20초 후 녹화 종료
        setTimeout(function(){
            recordData = recordData.substring(0, recordData.length - 1);
            axios.post('http://localhost:5000/analyze_raw', {
                data: recordData
            }, {timeout: 20000})
            .then((response) => {
                resData = response.data
                let result = {};
                result = {
                    reps: resData.reps,
                    majorProblems: resData.majorProblems,
                    minorProblems: resData.minorProblems,
                    strengths:  resData.strengths,
                    success: 1
                };
                res.json(result);
            })
            .catch((error) => {
                console.log("EVAL FAILED");
                result = {};
                result["success"] = 0;
                res.json(result);
            })               
        }, 20000);

    });

    app.get('/api/test', (req, res) =>  {
        console.log("clicked")
        sleep(2000);
        sleep(2000);
        let result = {};

        result = {
            reps: "10",
            majorProblems: ["knees_over_toes", "back_hip_angle"],
            minorProblems: ["squat_depth"],
            strengths: ["bend_hips_knees"]
        };
        result["success"] = 1;

        res.json(result);
    });

    kinect.openBodyReader();
}

