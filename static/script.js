// 获取视频、画布、按钮和图片元素
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const photo = document.getElementById('photo');

// 访问摄像头
navigator.mediaDevices.getUserMedia({ video: true })
   .then((stream) => {
        video.srcObject = stream;
    })
   .catch((error) => {
        console.error('无法访问摄像头:', error);
    });

// 拍照功能
captureButton.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const photoData = canvas.toDataURL('image/png');
    photo.src = photoData;

    // 发送照片数据到后端
    fetch('/save_photo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `photo=${encodeURIComponent(photoData)}`
    })
   .then((response) => response.text())
   .then((data) => {
        console.log(data);
        alert(data);
    })
   .catch((error) => {
        console.error('保存照片时出错:', error);
        alert('保存照片时出错:'+error);
    });
});