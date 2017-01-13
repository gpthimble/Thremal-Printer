from PIL import Image,ImageDraw,ImageFont
import sys,getopt,serial
textsize=40
printerlenth=384
totalpoints=textsize*printerlenth
totalbytes=totalpoints//8
bytesperline=printerlenth//8
fontname='times.ttf'
text=''
port='null'
alignX=0
alignY=0
im=Image.new('L',(printerlenth,textsize),color=0)
draw=ImageDraw.Draw(im)
font=ImageFont.truetype(font=fontname,size=int(textsize*0.8))
draw.text((alignX,alignY),text,fill=15,font=font)
im_data_list=list(im.getdata())


def get_bit(byteval,idx):

    return ((byteval&(1<<idx))!=0);

def set_bit(v, index, x):
  """Set the index:th bit of v to x, and return the new value."""
  mask = 1 << index
  v &= ~mask
  if x:
    v |= mask
  return v

def get_line(line):

    return im_data_list[(line)*printerlenth:(line+1)*printerlenth];

def get_point(line , row):

    return get_line(line)[row];

def get_sliced_point(line,row):

    return get_sliced_line(line)[row]

def slice_point(point):

    return [get_bit(point,3),get_bit(point,2),get_bit(point,1),get_bit(point,0)]

def get_sliced_data(data):
    sliced_data= []
    to_be_sliced_data=data
    for points in to_be_sliced_data:
        sliced_data.append(slice_point(points));
    return sliced_data

def get_sliced_line(line):

    return sliced_data[(line)*printerlenth:(line+1)*printerlenth];

def get_bytes(sliced):
    data_bytes=[]
    for byte in range(0,int(totalbytes)):
        num1=0
        num2=0
        num3=0
        num4=0
        for num in range(0,8):
            num1=set_bit(num1,7-num,sliced[(byte)*8+num][0])
            num2=set_bit(num2,7-num,sliced[(byte)*8+num][1])
            num3=set_bit(num3,7-num,sliced[(byte)*8+num][2])
            num4=set_bit(num4,7-num,sliced[(byte)*8+num][3])
        data_bytes.append([num1,num2,num3,num4])
    return data_bytes

def get_bytes_line(line):

    return(data_in_bytes[line*48:(line+1)*48])

def show_help():
        print('printer driver help')
        print('-h              --help              :show this message')
        print('-s <textsize>   --size <textsize>   :Set text size,Default is 40')
        print('-f <\'fontname\'> --font <\'fontname\'> :set font style Default is times.ttf')
        print('-p <\'port\'>     --port <\'port\'>     :set serial port numbner,eg:COM4')
        print('-t <\'text\'>     --text <\'text\'>     :texts to be printed.Default is \'hello world\'') 

def error_occured():
        print('error occured.')
        sys.exit(2)            

sliced_data=get_sliced_data(im_data_list)
data_in_bytes=get_bytes(sliced_data)

def main(argv):
    #print(sys.argv)
    global port
    global textsize
    global printerlenth
    global totalpoints
    global totalbytes
    global bytesperline
    global fontname
    global text
    global im
    global draw
    global font
    global im_data_list
    global sliced_data
    global data_in_bytes
    global alignX,alignY
    #deal with interface.
    try:
        opts,args=getopt.getopt(argv,"hs:f:p:t:X:Y:",["help","size=","font=","port=","text="])
    except getopt.GetoptError:
        print('Can\'t find option :',str(sys.argv[1:]))
        show_help()
        sys.exit(2)
    if len(sys.argv) == 1:
        show_help()
        sys.exit(2)
    for opt,arg in opts:
        if opt in ('-h','--help'):
            show_help()
            sys.exit()
        elif opt in ('-s','--size'):
            textsize=int(arg)
        elif opt in ('-f','--font'):
            fontname=arg
        elif opt in ('-p','--port'):
            port=arg
        elif opt in('-t','--text'):
            text=arg
        elif opt in ('-X'):
        	alignX=int(arg)
        elif opt in ('-Y'):
        	alignY=int(arg)
    if port=='null':
        print('please use -p(--port) to set correct serial port number.')
        sys.exit(2)
    totalpoints=textsize*printerlenth
    totalbytes=totalpoints//8
    bytesperline=printerlenth//8
    im=Image.new('L',(printerlenth,textsize),color=0)
    draw=ImageDraw.Draw(im)
    try:font=ImageFont.truetype(font=fontname,size=int(textsize*0.8))
    except BaseException:
    	print('Error occured:')
    	print('Uable to locate font file:',fontname,',use default instead.')
    	font=ImageFont.truetype(font='simsun.ttc',size=int(textsize*0.8))
    draw.text((alignX,alignY),text,fill=15,font=font)
    im_data_list=list(im.getdata())
    sliced_data=get_sliced_data(im_data_list)
    data_in_bytes=get_bytes(sliced_data)
    #setting up serial port
    uart=serial.Serial()
    uart.baudrate=115200
    uart.port=port
    uart.timeout=1
    try : uart.open()
    except	BaseException:
    	print('Error occured:')
    	print('Uable to open Serial Port:',port)
    	sys.exit(2)
    else:print ('Serial Port',port,'is opened')
    #begin communacation cycle
    state = 1
    tries = 0
    while 1 :
        #1st hand shaking with the printer
        if state ==1:
            if tries < 10:
                tries = tries +1
                print('trying to connect the printer in',tries,'atemps')
                uart.write(bytes([textsize]))
                if uart.read() != bytes([textsize]) : 
                    state = 1
                else :
                    state = 2
                    break

            else:
                print('communacation error occured.')
                sys.exit(2)
        
    if state == 2:
        print('connected,sending data')
        for line in range(0,textsize):
            line_waiting_for_sending=get_bytes_line(line)
            for byte in range(0,bytesperline):
                uart.write(bytes([line_waiting_for_sending[byte][0]]))
                #print(uart.read())              #for test useage
            print('scale0 sent,waiting for acknowledgement')
            #uart.write(b'\x01')                 #for test useage
            if uart.read()!=b'\x01':error_occured()
            else:
                for byte in range(0,bytesperline): 
                    uart.write(bytes([line_waiting_for_sending[byte][1]]))
                    #print(uart.read())          #for test useage
                print('scale1 sent,waiting for acknowledgement')
                #uart.write(b'\x02')             #for test useage
                if uart.read()!=b'\x02':error_occured()
                else:
                    for byte in range(0,bytesperline):
                        uart.write(bytes([line_waiting_for_sending[byte][2]]))
                        #print(uart.read())      #for test useage
                    print('scale2 sent, waiting for acknowledgement')
                    #uart.write(b'\x03')         #for test useage
                    if uart.read()!=b'\x03':error_occured()
                    else:
                        for byte in range(0,bytesperline):
                            uart.write(bytes([line_waiting_for_sending[byte][3]]))
                            #print(uart.read())  #for test useage
                        print('scale3 sent,waiting for acknowledgement')
                        #uart.write(b'\x04')     #for test useage
                        if uart.read()!=b'\x04':error_occured()
                        else:
                            print('line',line,'printed.')

    else : 
        error_occured()          
        

    print('done.')
    uart.close()
    print('Serial Port',port,"is closed")    
    sys.exit(0)
if __name__ == "__main__":
   main(sys.argv[1:])
