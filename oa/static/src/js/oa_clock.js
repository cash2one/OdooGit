/*!
 * JS电子时钟
 * 使用到的两个函数
 */
function startTime(){
    var today=new Date();
    var h=today.getHours();
    var m=today.getMinutes();
    var s=today.getSeconds();
    m=checkTime(m);
    s=checkTime(s);
    if(document.getElementById('time')){
	    document.getElementById('time').innerHTML=h+":"+m+":"+s;
	    setTimeout('startTime()',500);
    }
}
    
function checkTime(i){
    if (i<10) {i="0" + i}
    return i
}
    