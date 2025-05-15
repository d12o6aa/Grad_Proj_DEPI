let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');
let instruction = document.getElementById('instruction');

let stage = 0;
const stages = ["انظر مباشرة للكاميرا", "لف رأسك لليمين", "لف رأسك لليسار", "✔️ تم التسجيل"];

navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.srcObject = stream;
});

function capture() {
    context.drawImage(video, 0, 0, 640, 480);
    let image_data_url = canvas.toDataURL('image/jpeg');

    fetch('/save_frame', {
        method: 'POST',
        body: JSON.stringify({
            image: image_data_url,
            stage: stage
        }),
        headers: { 'Content-Type': 'application/json' }
    }).then(res => res.text())
      .then(data => {
        stage++;
        instruction.innerText = stages[stage];
    });
}
