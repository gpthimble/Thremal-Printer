//buffer for one line(48 bytes , long 384 points)
byte data[48]={0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0,
               0,0,0,0,0,0,0,0};
//pin mapping               
int p_data_in = 2;
int p_shift_clock=3;
int p_motor_enable=11;//5
int p_motor_dir_control=12;//6
int p_motor_step=13;//7
int p_latch=4;
int p_stroke1=14;//可以合并，stroke1-2=11，stroke3-4=10,stroke5-6=9
int p_stroke2=15;
int p_stroke3=16;
int p_stroke4=17;
int p_stroke5=18;
int p_stroke6=19;
//default motor direction
boolean motor_foward=true;
float multi_heat=1;
void setup()    //初始化
{
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(p_data_in,OUTPUT);
  pinMode(p_shift_clock,OUTPUT);
  pinMode(p_latch,OUTPUT);
  data_out();
  pinMode(p_stroke1, OUTPUT);
  digitalWrite(p_stroke1,LOW);
  pinMode(p_stroke2, OUTPUT);
  digitalWrite(p_stroke2,LOW);
  pinMode(p_stroke3, OUTPUT);
  digitalWrite(p_stroke3,LOW);
  pinMode(p_stroke4, OUTPUT);
  digitalWrite(p_stroke4,LOW);
  pinMode(p_stroke5, OUTPUT);
  digitalWrite(p_stroke5,LOW);
  pinMode(p_stroke6, OUTPUT);
  digitalWrite(p_stroke6,LOW);
  pinMode(p_motor_enable,OUTPUT);
  digitalWrite(p_motor_enable,HIGH);
  pinMode(p_motor_dir_control,OUTPUT);
  digitalWrite(p_motor_dir_control,LOW);
  pinMode(p_motor_step,OUTPUT);
  digitalWrite(p_motor_step,LOW);

  digitalWrite(p_motor_enable,LOW); 
    digitalWrite(p_motor_enable,HIGH);  
  Serial.begin(115200);
  //Serial.print('1');
  //delay(10000);
  }

void data_out() //shift out 48bytes long data
{
  digitalWrite(p_latch,HIGH);
  for (int i = 0; i < 48; ++i)
  {
    shiftOut(p_data_in,p_shift_clock,MSBFIRST,data[i]);
  }
  digitalWrite(p_latch,LOW);}

void motor_step (boolean motor_foward,int steps) //run motor 
{
  digitalWrite(p_motor_dir_control,motor_foward);
  for (int i = 0; i < steps; ++i)
  {
    delayMicroseconds(100);
    digitalWrite(p_motor_step,HIGH);
    delayMicroseconds(100);
    digitalWrite(p_motor_step,LOW);

  }}

void test_data(int paten1,int paten2)  //g
{
  for (int i = 0; i < 48; ++i)
  {
    data[i]=paten1;
  ++i;
  data[i]=paten2;
  }}

void print(int heat_time)
{
  digitalWrite(p_stroke1,HIGH);
  digitalWrite(p_stroke2,HIGH);
  digitalWrite(p_stroke3,HIGH);
  digitalWrite(p_stroke4,HIGH);
  digitalWrite(p_stroke5,HIGH);
  digitalWrite(p_stroke6,HIGH);
  delay(heat_time*multi_heat);
  digitalWrite(p_stroke1,LOW);
  digitalWrite(p_stroke2,LOW);
  digitalWrite(p_stroke3,LOW);
  digitalWrite(p_stroke4,LOW);
  digitalWrite(p_stroke5,LOW);
  digitalWrite(p_stroke6,LOW);
 }
// the loop function runs over and over again forever
int incomingByte=0;
int lines=0;
int state =0;
int i=0;
void loop() {
//data={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  if (state==0)
    { 
      while(1)
      {
        digitalWrite(p_motor_enable,HIGH);
                    //Serial.print('ready!');
        if (Serial.available() > 0) 
        {
          incomingByte = Serial.read();

            if (int(incomingByte)!=0)
              {
                lines=incomingByte;
                Serial.write(incomingByte);
                state=1;
                digitalWrite(p_motor_enable,LOW);
                break;
              }
        }
      }

    }
  else if (state ==1)
    {

      i=0;
      while (i < 48)
        {
          if (Serial.available()>0)
            {
              data[i]=Serial.read();
              i++;
            }
        }
      data_out();
      print(16);
      //motor_step(false,1);
      Serial.write(state);
      state = 2;
  }
  else if (state==2)  
    {
      i=0;
      while (i < 48)
        {
          if (Serial.available()>0)
            {
              data[i]=Serial.read();
              i++;
            }
        }
      data_out();
      print(8);
      //motor_step(false,1);
      Serial.write(state);
      state = 3;
    }
  else if (state==3)
    {
 
      i=0;
      while (i < 48)
        {
          if (Serial.available()>0)
            {
              data[i]=Serial.read();
              i++;
            }
        }
      data_out();
      print(4);
      //motor_step(false,1);
      Serial.write(state);
      state = 4;
    }

  else if (state ==4)
    {
      i=0;
      while (i < 48)
        {
          if (Serial.available()>0)
            {
              data[i]=Serial.read();
              i++;
            }
        }
      data_out();
      print(2);
      motor_step(false,4);
      Serial.write(state);
      lines=lines-1;
      if (lines==0)
      {
        state = 0;
      }
      else
        state = 1;
    }
  }

  
  

