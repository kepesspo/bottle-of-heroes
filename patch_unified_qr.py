#!/usr/bin/env python3
# v9.823 — unified offline QR join: local QR generator (Kazuhiko Arase
# qrcode-generator, MIT, byte mode + auto version + auto mask), shared RoomQR
# component, header round-counter QR button + MENU control-tab QR button.
import io, re

PATH = 'index.html'
with io.open(PATH, encoding='utf-8') as f:
    c = f.read()

edits = 0
def rep(old, new):
    global c, edits
    assert old in c, 'MISSING: ' + repr(old[:80])
    assert c.count(old) == 1, 'NOT UNIQUE (%d): %s' % (c.count(old), repr(old[:80]))
    c = c.replace(old, new)
    edits += 1

# ── 1. Local QR encoder — plain JS <script>, inserted right after the
#      firebase block, before the Spotify SDK. Exposes window.makeQRCanvas. ──
QR_JS = r'''</script>

<!-- Local (offline) QR code generator — Kazuhiko Arase qrcode-generator (MIT),
     byte mode, auto version (1-40), ECC level M, auto mask (best of 0-7). -->
<script>
(function(){
  var QRMode = { MODE_8BIT_BYTE: 1 << 2 };
  var QRErrorCorrectLevel = { L:1, M:0, Q:3, H:2 };
  var QRMaskPattern = { PATTERN000:0,PATTERN001:1,PATTERN010:2,PATTERN011:3,PATTERN100:4,PATTERN101:5,PATTERN110:6,PATTERN111:7 };

  var QRMath = (function(){
    var EXP = new Array(256), LOG = new Array(256), i;
    for (i=0;i<8;i++) EXP[i] = 1<<i;
    for (i=8;i<256;i++) EXP[i] = EXP[i-4]^EXP[i-5]^EXP[i-6]^EXP[i-8];
    for (i=0;i<255;i++) LOG[EXP[i]] = i;
    return {
      glog:function(n){ if(n<1) throw new Error('glog('+n+')'); return LOG[n]; },
      gexp:function(n){ while(n<0)n+=255; while(n>=256)n-=255; return EXP[n]; }
    };
  })();

  function qrPolynomial(num, shift){
    if (typeof num.length=='undefined') throw new Error(num.length+'/'+shift);
    var _num = (function(){
      var offset=0; while(offset<num.length && num[offset]==0) offset++;
      var n=new Array(num.length-offset+shift);
      for(var i=0;i<num.length-offset;i++) n[i]=num[i+offset];
      return n;
    })();
    var _this={};
    _this.getAt=function(i){return _num[i];};
    _this.getLength=function(){return _num.length;};
    _this.multiply=function(e){
      var out=new Array(_this.getLength()+e.getLength()-1);
      for(var i=0;i<_this.getLength();i++)
        for(var j=0;j<e.getLength();j++)
          out[i+j]^=QRMath.gexp(QRMath.glog(_this.getAt(i))+QRMath.glog(e.getAt(j)));
      return qrPolynomial(out,0);
    };
    _this.mod=function(e){
      if(_this.getLength()-e.getLength()<0) return _this;
      var ratio=QRMath.glog(_this.getAt(0))-QRMath.glog(e.getAt(0));
      var out=new Array(_this.getLength());
      for(var i=0;i<_this.getLength();i++) out[i]=_this.getAt(i);
      for(var i=0;i<e.getLength();i++) out[i]^=QRMath.gexp(QRMath.glog(e.getAt(i))+ratio);
      return qrPolynomial(out,0).mod(e);
    };
    return _this;
  }

  var QRUtil = (function(){
    var PATTERN_POSITION_TABLE=[[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],[6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],[6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],[6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],[6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,114,142],[6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,80,106,132,158],[6,32,58,84,110,136,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]];
    var G15=(1<<10)|(1<<8)|(1<<5)|(1<<4)|(1<<2)|(1<<1)|(1<<0);
    var G18=(1<<12)|(1<<11)|(1<<10)|(1<<9)|(1<<8)|(1<<5)|(1<<2)|(1<<0);
    var G15_MASK=(1<<14)|(1<<12)|(1<<10)|(1<<4)|(1<<1);
    function getBCHDigit(data){var d=0; while(data!=0){d++; data>>>=1;} return d;}
    return {
      getBCHTypeInfo:function(data){
        var d=data<<10;
        while(getBCHDigit(d)-getBCHDigit(G15)>=0) d^=(G15<<(getBCHDigit(d)-getBCHDigit(G15)));
        return ((data<<10)|d)^G15_MASK;
      },
      getBCHTypeNumber:function(data){
        var d=data<<12;
        while(getBCHDigit(d)-getBCHDigit(G18)>=0) d^=(G18<<(getBCHDigit(d)-getBCHDigit(G18)));
        return (data<<12)|d;
      },
      getPatternPosition:function(t){return PATTERN_POSITION_TABLE[t-1];},
      getMaskFunction:function(p){
        switch(p){
          case 0: return function(i,j){return (i+j)%2==0;};
          case 1: return function(i,j){return i%2==0;};
          case 2: return function(i,j){return j%3==0;};
          case 3: return function(i,j){return (i+j)%3==0;};
          case 4: return function(i,j){return (Math.floor(i/2)+Math.floor(j/3))%2==0;};
          case 5: return function(i,j){return (i*j)%2+(i*j)%3==0;};
          case 6: return function(i,j){return ((i*j)%2+(i*j)%3)%2==0;};
          case 7: return function(i,j){return ((i*j)%3+(i+j)%2)%2==0;};
          default: throw new Error('bad maskPattern:'+p);
        }
      },
      getErrorCorrectPolynomial:function(len){
        var a=qrPolynomial([1],0);
        for(var i=0;i<len;i++) a=a.multiply(qrPolynomial([1,QRMath.gexp(i)],0));
        return a;
      },
      getLengthInBits:function(mode,type){
        if(1<=type&&type<10) return 8;      // byte mode, v1-9
        else if(type<27) return 16;         // v10-26
        else if(type<41) return 16;         // v27-40
        else throw new Error('type:'+type);
      },
      getLostPoint:function(qr){
        var n=qr.getModuleCount(), lost=0, row, col, r, cc;
        for(row=0;row<n;row++) for(col=0;col<n;col++){
          var same=0, dark=qr.isDark(row,col);
          for(r=-1;r<=1;r++){ if(row+r<0||n<=row+r) continue;
            for(cc=-1;cc<=1;cc++){ if(col+cc<0||n<=col+cc) continue; if(r==0&&cc==0) continue;
              if(dark==qr.isDark(row+r,col+cc)) same++;
            }
          }
          if(same>5) lost+=(3+same-5);
        }
        for(row=0;row<n-1;row++) for(col=0;col<n-1;col++){
          var cnt=0;
          if(qr.isDark(row,col)) cnt++;
          if(qr.isDark(row+1,col)) cnt++;
          if(qr.isDark(row,col+1)) cnt++;
          if(qr.isDark(row+1,col+1)) cnt++;
          if(cnt==0||cnt==4) lost+=3;
        }
        for(row=0;row<n;row++) for(col=0;col<n-6;col++){
          if(qr.isDark(row,col)&&!qr.isDark(row,col+1)&&qr.isDark(row,col+2)&&qr.isDark(row,col+3)&&qr.isDark(row,col+4)&&!qr.isDark(row,col+5)&&qr.isDark(row,col+6)) lost+=40;
        }
        for(col=0;col<n;col++) for(row=0;row<n-6;row++){
          if(qr.isDark(row,col)&&!qr.isDark(row+1,col)&&qr.isDark(row+2,col)&&qr.isDark(row+3,col)&&qr.isDark(row+4,col)&&!qr.isDark(row+5,col)&&qr.isDark(row+6,col)) lost+=40;
        }
        var darkCount=0;
        for(col=0;col<n;col++) for(row=0;row<n;row++) if(qr.isDark(row,col)) darkCount++;
        var ratio=Math.abs(100*darkCount/n/n-50)/5;
        lost+=ratio*10;
        return lost;
      }
    };
  })();

  var QRRSBlock = (function(){
    var T=[
      [1,26,19],[1,26,16],[1,26,13],[1,26,9],
      [1,44,34],[1,44,28],[1,44,22],[1,44,16],
      [1,70,55],[1,70,44],[2,35,17],[2,35,13],
      [1,100,80],[2,50,32],[2,50,24],[4,25,9],
      [1,134,108],[2,67,43],[2,33,15,2,34,16],[2,33,11,2,34,12],
      [2,86,68],[4,43,27],[4,43,19],[4,43,15],
      [2,98,78],[4,49,31],[2,32,14,4,33,15],[4,39,13,1,40,14],
      [2,121,97],[2,60,38,2,61,39],[4,40,18,2,41,19],[4,40,14,2,41,15],
      [2,146,116],[3,58,36,2,59,37],[4,36,16,4,37,17],[4,36,12,4,37,13],
      [2,86,68,2,87,69],[4,69,43,1,70,44],[6,43,19,2,44,20],[6,43,15,2,44,16],
      [4,101,81],[1,80,50,4,81,51],[4,50,22,4,51,23],[3,36,12,8,37,13],
      [2,116,92,2,117,93],[6,58,36,2,59,37],[4,46,20,6,47,21],[7,42,14,4,43,15],
      [4,133,107],[8,59,37,1,60,38],[8,44,20,4,45,21],[12,33,11,4,34,12],
      [3,145,115,1,146,116],[4,64,40,5,65,41],[11,36,16,5,37,17],[11,36,12,5,37,13],
      [5,109,87,1,110,88],[5,65,41,5,66,42],[5,54,24,7,55,25],[11,36,12,7,37,13],
      [5,122,98,1,123,99],[7,73,45,3,74,46],[15,43,19,2,44,20],[3,45,15,13,46,16],
      [1,135,107,5,136,108],[10,74,46,1,75,47],[1,50,22,15,51,23],[2,42,14,17,43,15],
      [5,150,120,1,151,121],[9,69,43,4,70,44],[17,50,22,1,51,23],[2,42,14,19,43,15],
      [3,141,113,4,142,114],[3,70,44,11,71,45],[17,47,21,4,48,22],[9,39,13,16,40,14],
      [3,135,107,5,136,108],[3,67,41,13,68,42],[15,54,24,5,55,25],[15,43,15,10,44,16],
      [4,144,116,4,145,117],[17,68,42],[17,50,22,6,51,23],[19,46,16,6,47,17],
      [2,139,111,7,140,112],[17,74,46],[7,54,24,16,55,25],[34,37,13],
      [4,151,121,5,152,122],[4,75,47,14,76,48],[11,54,24,14,55,25],[16,45,15,14,46,16],
      [6,147,117,4,148,118],[6,73,45,14,74,46],[11,54,24,16,55,25],[30,46,16,2,47,17],
      [8,132,106,4,133,107],[8,75,47,13,76,48],[7,54,24,22,55,25],[22,45,15,13,46,16],
      [10,142,114,2,143,115],[19,74,46,4,75,47],[28,50,22,6,51,23],[33,46,16,4,47,17],
      [8,152,122,4,153,123],[22,73,45,3,74,46],[8,53,23,26,54,24],[12,45,15,28,46,16],
      [3,147,117,10,148,118],[3,73,45,23,74,46],[4,54,24,31,55,25],[11,45,15,31,46,16],
      [7,146,116,7,147,117],[21,73,45,7,74,46],[1,53,23,37,54,24],[19,45,15,26,46,16],
      [5,145,115,10,146,116],[19,75,47,10,76,48],[15,54,24,25,55,25],[23,45,15,25,46,16],
      [13,145,115,3,146,116],[2,74,46,29,75,47],[42,54,24,1,55,25],[23,45,15,28,46,16],
      [17,145,115],[10,74,46,23,75,47],[10,54,24,35,55,25],[19,45,15,35,46,16],
      [17,145,115,1,146,116],[14,74,46,21,75,47],[29,54,24,19,55,25],[11,45,15,46,46,16],
      [13,145,115,6,146,116],[14,74,46,23,75,47],[44,54,24,7,55,25],[59,46,16,1,47,17],
      [12,151,121,7,152,122],[12,75,47,26,76,48],[39,54,24,14,55,25],[22,45,15,41,46,16],
      [6,151,121,14,152,122],[6,75,47,34,76,48],[46,54,24,10,55,25],[2,45,15,64,46,16],
      [17,152,122,4,153,123],[29,74,46,14,75,47],[49,54,24,10,55,25],[24,45,15,46,46,16],
      [4,152,122,18,153,123],[13,74,46,32,75,47],[48,54,24,14,55,25],[42,45,15,32,46,16],
      [20,147,117,4,148,118],[40,75,47,7,76,48],[43,54,24,22,55,25],[10,45,15,67,46,16],
      [19,148,118,6,149,119],[18,75,47,31,76,48],[34,54,24,34,55,25],[20,45,15,61,46,16]
    ];
    function tbl(type, level){
      var off = (level==QRErrorCorrectLevel.L)?0:(level==QRErrorCorrectLevel.M)?1:(level==QRErrorCorrectLevel.Q)?2:(level==QRErrorCorrectLevel.H)?3:-1;
      if(off<0) return undefined;
      return T[(type-1)*4+off];
    }
    return {
      getRSBlocks:function(type, level){
        var rs=tbl(type, level);
        if(typeof rs=='undefined') throw new Error('bad rs block @ type:'+type+'/level:'+level);
        var len=rs.length/3, list=[];
        for(var i=0;i<len;i++){
          var count=rs[i*3+0], total=rs[i*3+1], data=rs[i*3+2];
          for(var j=0;j<count;j++) list.push({ totalCount:total, dataCount:data });
        }
        return list;
      }
    };
  })();

  function qrBitBuffer(){
    var buf=[], len=0, _this={};
    _this.getBuffer=function(){return buf;};
    _this.put=function(num,length){ for(var i=0;i<length;i++) _this.putBit(((num>>>(length-i-1))&1)==1); };
    _this.getLengthInBits=function(){return len;};
    _this.putBit=function(bit){
      var idx=Math.floor(len/8);
      if(buf.length<=idx) buf.push(0);
      if(bit) buf[idx]|=(0x80>>>(len%8));
      len++;
    };
    return _this;
  }

  function utf8Bytes(s){
    var b=[];
    for(var i=0;i<s.length;i++){
      var c=s.charCodeAt(i);
      if(c<0x80) b.push(c);
      else if(c<0x800){ b.push(0xc0|(c>>6),0x80|(c&0x3f)); }
      else if(c<0xd800||c>=0xe000){ b.push(0xe0|(c>>12),0x80|((c>>6)&0x3f),0x80|(c&0x3f)); }
      else { i++; var cp=0x10000+((c&0x3ff)<<10)+(s.charCodeAt(i)&0x3ff); b.push(0xf0|(cp>>18),0x80|((cp>>12)&0x3f),0x80|((cp>>6)&0x3f),0x80|(cp&0x3f)); }
    }
    return b;
  }

  function qr8BitByte(data){
    var bytes=utf8Bytes(data);
    return {
      getMode:function(){return QRMode.MODE_8BIT_BYTE;},
      getLength:function(){return bytes.length;},
      write:function(buffer){ for(var i=0;i<bytes.length;i++) buffer.put(bytes[i],8); }
    };
  }

  function qrcode(typeNumber, ecl){
    var PAD0=0xEC, PAD1=0x11;
    var _typeNumber=typeNumber;
    var _ecl=QRErrorCorrectLevel[ecl];
    var _modules=null, _moduleCount=0, _dataCache=null, _dataList=[];
    var _this={};

    function setupPositionProbePattern(row,col){
      for(var r=-1;r<=7;r++){ if(row+r<=-1||_moduleCount<=row+r) continue;
        for(var cc=-1;cc<=7;cc++){ if(col+cc<=-1||_moduleCount<=col+cc) continue;
          _modules[row+r][col+cc]=((0<=r&&r<=6&&(cc==0||cc==6))||(0<=cc&&cc<=6&&(r==0||r==6))||(2<=r&&r<=4&&2<=cc&&cc<=4));
        }
      }
    }
    function setupTimingPattern(){
      for(var r=8;r<_moduleCount-8;r++){ if(_modules[r][6]!=null) continue; _modules[r][6]=(r%2==0); }
      for(var cc=8;cc<_moduleCount-8;cc++){ if(_modules[6][cc]!=null) continue; _modules[6][cc]=(cc%2==0); }
    }
    function setupPositionAdjustPattern(){
      var pos=QRUtil.getPatternPosition(_typeNumber);
      for(var i=0;i<pos.length;i++) for(var j=0;j<pos.length;j++){
        var row=pos[i], col=pos[j];
        if(_modules[row][col]!=null) continue;
        for(var r=-2;r<=2;r++) for(var cc=-2;cc<=2;cc++)
          _modules[row+r][col+cc]=(r==-2||r==2||cc==-2||cc==2||(r==0&&cc==0));
      }
    }
    function setupTypeNumber(test){
      var bits=QRUtil.getBCHTypeNumber(_typeNumber), i, mod;
      for(i=0;i<18;i++){ mod=(!test&&((bits>>i)&1)==1); _modules[Math.floor(i/3)][i%3+_moduleCount-8-3]=mod; }
      for(i=0;i<18;i++){ mod=(!test&&((bits>>i)&1)==1); _modules[i%3+_moduleCount-8-3][Math.floor(i/3)]=mod; }
    }
    function setupTypeInfo(test, maskPattern){
      var data=(_ecl<<3)|maskPattern, bits=QRUtil.getBCHTypeInfo(data), i, mod;
      for(i=0;i<15;i++){ mod=(!test&&((bits>>i)&1)==1);
        if(i<6) _modules[i][8]=mod; else if(i<8) _modules[i+1][8]=mod; else _modules[_moduleCount-15+i][8]=mod;
      }
      for(i=0;i<15;i++){ mod=(!test&&((bits>>i)&1)==1);
        if(i<8) _modules[8][_moduleCount-i-1]=mod; else if(i<9) _modules[8][15-i-1+1]=mod; else _modules[8][15-i-1]=mod;
      }
      _modules[_moduleCount-8][8]=(!test);
    }
    function mapData(data, maskPattern){
      var inc=-1, row=_moduleCount-1, bitIndex=7, byteIndex=0;
      var maskFunc=QRUtil.getMaskFunction(maskPattern);
      for(var col=_moduleCount-1;col>0;col-=2){
        if(col==6) col-=1;
        while(true){
          for(var cc=0;cc<2;cc++){
            if(_modules[row][col-cc]==null){
              var dark=false;
              if(byteIndex<data.length) dark=(((data[byteIndex]>>>bitIndex)&1)==1);
              if(maskFunc(row,col-cc)) dark=!dark;
              _modules[row][col-cc]=dark;
              bitIndex--;
              if(bitIndex==-1){ byteIndex++; bitIndex=7; }
            }
          }
          row+=inc;
          if(row<0||_moduleCount<=row){ row-=inc; inc=-inc; break; }
        }
      }
    }
    function createBytes(buffer, rsBlocks){
      var offset=0, maxDc=0, maxEc=0;
      var dcdata=new Array(rsBlocks.length), ecdata=new Array(rsBlocks.length);
      for(var r=0;r<rsBlocks.length;r++){
        var dcCount=rsBlocks[r].dataCount, ecCount=rsBlocks[r].totalCount-dcCount;
        maxDc=Math.max(maxDc,dcCount); maxEc=Math.max(maxEc,ecCount);
        dcdata[r]=new Array(dcCount);
        for(var i=0;i<dcdata[r].length;i++) dcdata[r][i]=0xff&buffer.getBuffer()[i+offset];
        offset+=dcCount;
        var rsPoly=QRUtil.getErrorCorrectPolynomial(ecCount);
        var rawPoly=qrPolynomial(dcdata[r], rsPoly.getLength()-1);
        var modPoly=rawPoly.mod(rsPoly);
        ecdata[r]=new Array(rsPoly.getLength()-1);
        for(var i=0;i<ecdata[r].length;i++){
          var mi=i+modPoly.getLength()-ecdata[r].length;
          ecdata[r][i]=(mi>=0)?modPoly.getAt(mi):0;
        }
      }
      var total=0; for(var i=0;i<rsBlocks.length;i++) total+=rsBlocks[i].totalCount;
      var data=new Array(total), index=0;
      for(var i=0;i<maxDc;i++) for(var r=0;r<rsBlocks.length;r++) if(i<dcdata[r].length){ data[index]=dcdata[r][i]; index++; }
      for(var i=0;i<maxEc;i++) for(var r=0;r<rsBlocks.length;r++) if(i<ecdata[r].length){ data[index]=ecdata[r][i]; index++; }
      return data;
    }
    function createData(typeNumber, ecl, dataList){
      var rsBlocks=QRRSBlock.getRSBlocks(typeNumber, ecl);
      var buffer=qrBitBuffer();
      for(var i=0;i<dataList.length;i++){
        var d=dataList[i];
        buffer.put(d.getMode(),4);
        buffer.put(d.getLength(),QRUtil.getLengthInBits(d.getMode(),typeNumber));
        d.write(buffer);
      }
      var totalDataCount=0;
      for(var i=0;i<rsBlocks.length;i++) totalDataCount+=rsBlocks[i].dataCount;
      if(buffer.getLengthInBits()>totalDataCount*8) throw new Error('code length overflow.');
      if(buffer.getLengthInBits()+4<=totalDataCount*8) buffer.put(0,4);
      while(buffer.getLengthInBits()%8!=0) buffer.putBit(false);
      while(true){
        if(buffer.getLengthInBits()>=totalDataCount*8) break;
        buffer.put(PAD0,8);
        if(buffer.getLengthInBits()>=totalDataCount*8) break;
        buffer.put(PAD1,8);
      }
      return createBytes(buffer, rsBlocks);
    }
    function makeImpl(test, maskPattern){
      _moduleCount=_typeNumber*4+17;
      _modules=(function(mc){ var m=new Array(mc);
        for(var row=0;row<mc;row++){ m[row]=new Array(mc); for(var col=0;col<mc;col++) m[row][col]=null; }
        return m; })(_moduleCount);
      setupPositionProbePattern(0,0);
      setupPositionProbePattern(_moduleCount-7,0);
      setupPositionProbePattern(0,_moduleCount-7);
      setupPositionAdjustPattern();
      setupTimingPattern();
      setupTypeInfo(test, maskPattern);
      if(_typeNumber>=7) setupTypeNumber(test);
      if(_dataCache==null) _dataCache=createData(_typeNumber,_ecl,_dataList);
      mapData(_dataCache, maskPattern);
    }
    function getBestMaskPattern(){
      var minLost=0, pattern=0;
      for(var i=0;i<8;i++){
        makeImpl(true,i);
        var lost=QRUtil.getLostPoint(_this);
        if(i==0||minLost>lost){ minLost=lost; pattern=i; }
      }
      return pattern;
    }
    _this.addData=function(data){ _dataList.push(qr8BitByte(data)); _dataCache=null; };
    _this.isDark=function(row,col){
      if(row<0||_moduleCount<=row||col<0||_moduleCount<=col) throw new Error(row+','+col);
      return _modules[row][col];
    };
    _this.getModuleCount=function(){ return _moduleCount; };
    _this.make=function(){
      if(_typeNumber<1){
        var type=1;
        for(;type<40;type++){
          var rsBlocks=QRRSBlock.getRSBlocks(type,_ecl);
          var buffer=qrBitBuffer();
          for(var i=0;i<_dataList.length;i++){
            var d=_dataList[i];
            buffer.put(d.getMode(),4);
            buffer.put(d.getLength(),QRUtil.getLengthInBits(d.getMode(),type));
            d.write(buffer);
          }
          var totalDataCount=0;
          for(var i=0;i<rsBlocks.length;i++) totalDataCount+=rsBlocks[i].dataCount;
          if(buffer.getLengthInBits()<=totalDataCount*8) break;
        }
        _typeNumber=type;
      }
      makeImpl(false, getBestMaskPattern());
    };
    return _this;
  }

  // Public API: returns an HTMLCanvasElement with the QR (black on white, quiet zone).
  window.makeQRCanvas = function(text, sizePx){
    sizePx = sizePx || 220;
    var qr = qrcode(0, 'M');
    qr.addData(String(text));
    qr.make();
    var count = qr.getModuleCount();
    var quiet = 4;
    var total = count + quiet*2;
    var cell = Math.max(1, Math.floor(sizePx/total));
    var dim = cell*total;
    var canvas = document.createElement('canvas');
    canvas.width = dim; canvas.height = dim;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0,0,dim,dim);
    ctx.fillStyle = '#141424';
    for(var r=0;r<count;r++) for(var col=0;col<count;col++){
      if(qr.isDark(r,col)) ctx.fillRect((col+quiet)*cell,(r+quiet)*cell,cell,cell);
    }
    return canvas;
  };
  window.makeQRDataURL = function(text, sizePx){
    return window.makeQRCanvas(text, sizePx).toDataURL('image/png');
  };
})();
</script>

<!-- Spotify Web Playback SDK -->'''

rep('''</script>

<!-- Spotify Web Playback SDK -->''', QR_JS)

# ── 2. Shared RoomQR component + QRModal delegates to it ──
OLD_QRMODAL = '''function QRModal({ url, onClose }) {
  const roomCode = url.split('room=')[1] || '';
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=141424&bgcolor=ffffff&data=${encodeURIComponent(url)}`;
  return (
    <div onClick={onClose} style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.72)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:9999,padding:24}}>
      <div onClick={e=>e.stopPropagation()} style={{background:T.surface,borderRadius:24,padding:28,display:'flex',flexDirection:'column',alignItems:'center',gap:14,width:'100%',maxWidth:300,boxShadow:'0 8px 40px rgba(0,0,0,0.4)'}}>
        <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:17,color:T.ink}}>Csatlakozási QR kód</div>
        <img src={qrUrl} width={200} height={200} style={{borderRadius:12,border:`2px solid ${T.surfaceMuted}`}} alt="QR" />
        <div style={{fontFamily:'monospace',fontWeight:700,fontSize:26,color:T.mint,letterSpacing:'0.18em'}}>{roomCode}</div>
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',lineHeight:1.5}}>{t('busQrSub')}</div>
        <button onClick={onClose} style={{width:'100%',padding:'12px',background:T.mint,color:'#fff',border:'none',borderRadius:12,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,cursor:'pointer'}}>{t('busClose')}</button>
      </div>
    </div>
  );
}'''

NEW_QRMODAL = '''function RoomQR({ roomCode, onClose }) {
  const url = location.origin + location.pathname + '?room=' + roomCode;
  const wrapRef = React.useRef(null);
  const [fallback, setFallback] = React.useState(false);
  React.useEffect(() => {
    const wrap = wrapRef.current;
    if (!wrap) return;
    wrap.innerHTML = '';
    try {
      if (typeof window.makeQRCanvas !== 'function') throw new Error('no local QR encoder');
      const cv = window.makeQRCanvas(url, 220);
      cv.style.width = '220px'; cv.style.height = '220px';
      cv.style.borderRadius = '12px';
      cv.style.imageRendering = 'pixelated';
      cv.style.border = `2px solid ${T.surfaceMuted}`;
      wrap.appendChild(cv);
    } catch (e) {
      setFallback(true);
    }
  }, [url]);
  const copyLink = () => {
    if (navigator.share) { navigator.share({ title:'Bottle of Heroes', text:'Csatlakozz a meccshez!', url }).catch(()=>{}); }
    else if (navigator.clipboard) { navigator.clipboard.writeText(url).then(()=>alert('Link másolva! 🔗')).catch(()=>alert(url)); }
    else { alert(url); }
  };
  return (
    <div onClick={onClose} style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.72)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:9999,padding:24}}>
      <div onClick={e=>e.stopPropagation()} style={{background:T.surface,borderRadius:24,padding:28,display:'flex',flexDirection:'column',alignItems:'center',gap:14,width:'100%',maxWidth:320,boxShadow:'0 8px 40px rgba(0,0,0,0.4)'}}>
        <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:17,color:T.ink}}>Csatlakozási QR kód</div>
        <div ref={wrapRef} style={{width:220,height:220,display:'grid',placeItems:'center',background:'#fff',borderRadius:12,overflow:'hidden'}}>
          {fallback && <img src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&color=141424&bgcolor=ffffff&data=${encodeURIComponent(url)}`} width={220} height={220} style={{borderRadius:12,border:`2px solid ${T.surfaceMuted}`}} alt="QR" />}
        </div>
        <div style={{fontFamily:'monospace',fontWeight:700,fontSize:28,color:T.mint,letterSpacing:'0.18em'}}>{roomCode}</div>
        <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',lineHeight:1.5}}>{t('busQrSub')}</div>
        <button onClick={copyLink} style={{width:'100%',padding:'12px',background:T.mint,color:'#fff',border:'none',borderRadius:12,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,cursor:'pointer'}}>🔗 Link másolása</button>
        <button onClick={onClose} style={{width:'100%',padding:'11px',background:'transparent',color:T.inkSoft,border:`1.5px solid ${T.surfaceMuted}`,borderRadius:12,fontFamily:T.font,fontWeight:700,fontSize:14,cursor:'pointer'}}>{t('busClose')}</button>
      </div>
    </div>
  );
}

function QRModal({ url, onClose }) {
  const roomCode = (url.split('room=')[1] || '').split('&')[0];
  return <RoomQR roomCode={roomCode} onClose={onClose} />;
}'''

rep(OLD_QRMODAL, NEW_QRMODAL)

# ── 3. Busz — replace bespoke inline qrserver modal with shared RoomQR ──
OLD_BUSZ = '''      {showQR && roomCode && (
        <div onClick={()=>setShowQR(false)} style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.72)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:200,padding:24}}>
          <div onClick={e=>e.stopPropagation()} style={{background:T.surface,borderRadius:24,padding:28,display:'flex',flexDirection:'column',alignItems:'center',gap:14,width:'100%',maxWidth:300,boxShadow:'0 8px 40px rgba(0,0,0,0.4)'}}>
            <div style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:17,color:T.ink}}>Csatlakozási QR kód</div>
            <img src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=141424&bgcolor=FBEFD8&data=${encodeURIComponent(window.location.href.split('?')[0]+'?room='+roomCode)}`} width={200} height={200} style={{borderRadius:12,border:`2px solid ${T.surfaceMuted}`}} alt="QR" />
            <div style={{fontFamily:'monospace',fontWeight:700,fontSize:26,color:T.mint,letterSpacing:'0.18em'}}>{roomCode}</div>
            <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft,textAlign:'center',lineHeight:1.5}}>{t('busQrSub')}</div>
            <button onClick={()=>setShowQR(false)} style={{width:'100%',padding:'12px',background:T.mint,color:'#fff',border:'none',borderRadius:12,fontFamily:T.font,fontWeight:T.weightTitle,fontSize:15,cursor:'pointer'}}>{t('busClose')}</button>
          </div>
        </div>
      )}'''

NEW_BUSZ = '''      {showQR && roomCode && <RoomQR roomCode={roomCode} onClose={()=>setShowQR(false)} />}'''

rep(OLD_BUSZ, NEW_BUSZ)

# ── 4. PlayScreen: showRoomQR state ──
rep('  const [showInfo, setShowInfo] = useState(false);',
    '  const [showInfo, setShowInfo] = useState(false);\n  const [showRoomQR, setShowRoomQR] = useState(false);')

# ── 5. PlayScreen: render RoomQR modal (near top of return, before top bar) ──
rep('''      {/* ── Top bar ── */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>''',
    '''      {showRoomQR && roomCode && <RoomQR roomCode={roomCode} onClose={() => setShowRoomQR(false)} />}

      {/* ── Top bar ── */}
      <div style={{ flexShrink:0, display:'flex', alignItems:'center', gap:8, paddingTop:12, paddingBottom:6, paddingLeft:16, paddingRight:16, maxWidth:960, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>''')

# ── 6. PlayScreen: small QR button on the round-counter ring (online only) ──
OLD_RING = '''              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color: isInfinite ? T.coral : T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color: isInfinite ? T.coral : T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
              </div>
            </div>'''

NEW_RING = '''              <div style={{ position:'absolute', inset:6, background:T.surface, borderRadius:'50%', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                <div style={{ fontFamily:T.font, fontSize:8, fontWeight:700, color: isInfinite ? T.coral : T.inkSoft, letterSpacing:'0.07em', lineHeight:1 }}>{t('roundLabel')}</div>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:17, color: isInfinite ? T.coral : T.ink, lineHeight:1.1, fontVariantNumeric:'tabular-nums' }}>{round}</div>
              </div>
              {roomCode && (
                <button onClick={() => setShowRoomQR(true)} title="QR kód — csatlakozás" style={{ position:'absolute', right:-3, bottom:-3, width:22, height:22, borderRadius:'50%', border:`2px solid ${T.surface}`, background:T.mint, color:'#fff', cursor:'pointer', display:'grid', placeItems:'center', boxShadow:'0 2px 6px rgba(0,0,0,0.25)', padding:0, zIndex:3 }}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                </button>
              )}
            </div>'''

rep(OLD_RING, NEW_RING)

# ── 7. MENÜ Vezérlés tab: QR button next to room-code share row ──
OLD_MENU = '''                    <button onClick={() => {
                      const url = `${location.origin}${location.pathname}?room=${roomCode}`;
                      if (navigator.share) { navigator.share({ title:'Bottle of Heroes', text:'Csatlakozz a meccshez!', url }); }
                      else { navigator.clipboard?.writeText(url).then(() => alert('Link másolva! 🔗')).catch(() => alert(url)); }
                    }} style={{ width:34, height:34, borderRadius:10, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.inkSoft }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    </button>'''

NEW_MENU = '''                    <button onClick={() => setShowRoomQR(true)} title="QR kód" style={{ width:34, height:34, borderRadius:10, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.inkSoft }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h6v6H3V3zm2 2v2h2V5H5zm8-2h6v6h-6V3zm2 2v2h2V5h-2zM3 15h6v6H3v-6zm2 2v2h2v-2H5zm10-2h2v2h-2v-2zm4 0h2v2h-2v-2zm-4 4h2v2h-2v-2zm2 2h2v2h-2v-2zm2-2h2v2h-2v-2z"/></svg>
                    </button>
                    <button onClick={() => {
                      const url = `${location.origin}${location.pathname}?room=${roomCode}`;
                      if (navigator.share) { navigator.share({ title:'Bottle of Heroes', text:'Csatlakozz a meccshez!', url }); }
                      else { navigator.clipboard?.writeText(url).then(() => alert('Link másolva! 🔗')).catch(() => alert(url)); }
                    }} style={{ width:34, height:34, borderRadius:10, border:'none', background:'transparent', cursor:'pointer', display:'grid', placeItems:'center', flexShrink:0, color:T.inkSoft }}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                    </button>'''

rep(OLD_MENU, NEW_MENU)

# ── 8. Version bump ──
rep("const APP_VERSION = 'v9.822';", "const APP_VERSION = 'v9.823';")

assert edits == 8, 'expected 8 edits, got %d' % edits
with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(c)
print('patch_unified_qr applied OK, edits =', edits)
