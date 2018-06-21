#include <SPI.h>
#include <Wire.h>
#include <MsTimer2.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <mcp2515.h>
//#include <OneWire.h>
//#include <DallasTemperature.h>

//#define PB1               3
//#define PB2               8
#define KS                2
#define PowerOn           4
#define Enable_Auto       3
#define Enable_Drive      5
#define Enable12V_MCU     7
#define Piezo             10
//#define LED1              11
#define LED2              13
//#define ONE_WIRE_BUS      13
#define Current_Computers A7
#define Current_Drive     A6
#define Cell4             A3
#define Cell3             A2
#define Cell2             A1
#define Cell1             A0
//#define TEMPERATURE_PRECISION 9
#define OLED_RESET        7

//OneWire oneWire(ONE_WIRE_BUS);
//DallasTemperature sensors(&oneWire);
//DeviceAddress MOSFET_Thermometer, Battery_Thermometer;

Adafruit_SSD1306 display(OLED_RESET);

//A4 & A5 = SDA & SCL

volatile bool killToggle = true;
volatile bool underVoltage = false;
volatile bool overVoltage = false;
volatile bool updateFlag = false;
volatile float Cell1_Voltage;
volatile float Cell2_Voltage;
volatile float Cell3_Voltage;
volatile float Cell4_Voltage;
volatile float Total_Voltage;
static float driveCurrentOffset = 0.6;
static float computersCurrentOffset = 0.65;
volatile float driveCurrent;
volatile float computerCurrent;
volatile int temperature1;
volatile int temperature2;
volatile int temperature3;
volatile int displayState = 0;
volatile int killTimer = 0;
static float overCurrentLimit = 150.0;
volatile int overCurrentCounter;

struct can_frame canRxMsg;
struct can_frame canTxMsg;
struct can_frame canAutoMsg;
MCP2515 mcp2515(10);

void setup() {
  pinMode(KS, INPUT);
  pinMode(Enable_Auto, INPUT);
  attachInterrupt(digitalPinToInterrupt(KS), toggleKS, RISING);
  attachInterrupt(digitalPinToInterrupt(Enable_Auto), toggleAuto, RISING);
  //pinMode(PB1, INPUT);
  pinMode(Current_Drive, INPUT);
  pinMode(Cell1, INPUT);
  pinMode(Cell2, INPUT);
  pinMode(Cell3, INPUT);
  pinMode(Cell4, INPUT);

  pinMode(PowerOn, OUTPUT);
  pinMode(Enable_Drive, OUTPUT);
  //pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  //sensors.begin();
  Serial.begin(9600);

  SPI.beginTransaction(SPISettings(20000000, MSBFIRST, SPI_MODE0));
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS);
  mcp2515.setNormalMode();
  
  digitalWrite(PowerOn, HIGH);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  //TCCR1B = (TCCR1B & 0b11111000) | 0x02;
  /*analogWrite(Piezo, 80);
  delay(300);
  analogWrite(Piezo, 100);
  delay(300);
  analogWrite(Piezo, 127);
  delay(300);
  analogWrite(Piezo, 0);*/
  
  MsTimer2::set(500, updateAll); // 500ms period
  MsTimer2::start();
}

void loop() {
  //digitalWrite(LED1, HIGH);
  digitalWrite(PowerOn, HIGH);
  if (killToggle == true)
  {
    kill();
  }
  else if (killToggle == false)
  {
    unkill();
  }

  if(Total_Voltage <= 12){
    killToggle = true;
  }
  
  if(mcp2515.readMessage(&canRxMsg) == MCP2515::ERROR_OK){
    //Serial.println("Got Can Message");
    //Serial.println("Old ID was " + String(canRxMsg.can_id));
    if((canRxMsg.can_id & 0x3FF) - 641 == 0){ //Can't do a ==, need to have the difference be 0
      canTxMsg.can_id = 648;
      //Serial.println("Old ID was " + String(canRxMsg.can_id));
      //Serial.println("New ID is " + String(canTxMsg.can_id));
      canTxMsg.can_dlc = 2;
      canTxMsg.data[0] = byte(int(Total_Voltage));
      canTxMsg.data[1] = byte((Total_Voltage*100) - int(Total_Voltage)*100);
      //Serial.println("First Piece is " + String(canTxMsg.data[0]));
      //Serial.println("Second piece is " + String(canTxMsg.data[1]));
      MCP2515::ERROR rc = mcp2515.sendMessage(&canTxMsg);
      //Serial.println("Error was " + String(rc));
    }
  }

  while(mcp2515.checkError()){
      Serial.println("There was an error");
      mcp2515.reset();
      mcp2515.setBitrate(CAN_500KBPS);
      mcp2515.setNormalMode();
    }
  
  if (updateFlag == true)
  {
    //if(digitalRead(LED1) == HIGH)digitalWrite(LED2,LOW);
    //else if(digitalRead(LED1) == HIGH)digitalWrite(LED2,HIGH);
    TIMSK2 = 0; //Pause Timer2 Interrupt
    readVoltages();
    readCurrent();
    updateFlag = false;
    sendData();
    updateDisplay();
    serialCommand();

    if(killTimer > 0)
    {
      killTimer = 0;
    }
    
    /*if (digitalRead(PB1) == HIGH)
    {
      analogWrite(Piezo, 125);
      delay(100);
      int n;
      while(digitalRead(PB1) == HIGH)
      {
        if(n >= 20)
        {
          if (killToggle == true) killToggle = false;
          else if (killToggle == false) killToggle = true;
          break;
        }
        delay(20);
        n++;
      }
      analogWrite(Piezo, 0);
    }
    if (digitalRead(PB2) == HIGH)
    {
      analogWrite(Piezo, 125);
      int n;
      while(digitalRead(PB2) == HIGH)
      {
        analogWrite(Piezo, 155);
        
        if(n >= 20)
        {
          displayState = 2;
          updateDisplay();
          delay(2000);
          digitalWrite(PowerOn, LOW);
          delay(10000);
        }
        delay(50);
        analogWrite(Piezo, 0);
        delay(50);
        n++;
      }
    }*/
    TIMSK2 |= (1 << TOIE2); //Resume Timer2 Interrupt
  }
  //delay(0);
}

void serialCommand()
{
  while (Serial.available() > 0)
  {
    byte firstByte = Serial.read();
    if (firstByte == 0x11)
    {
      //Kill Sub
      kill();
    }
    else if (firstByte == 0x12)
    {
      //Unkill Sub
      unkill();
    }
    else if (firstByte == 0x13)
    {
      //Restart Computers
      computerRestart();
    }
  }
}
void kill()
{
  displayState = 1;
  digitalWrite(PowerOn, LOW);
  //digitalWrite(Enable_Computers, LOW);
  digitalWrite(Enable12V_MCU, HIGH);
  //Serial.println("Killed");
  //alarm(1);
  digitalWrite(LED2, HIGH);
}

void unkill()
{
  displayState = 0;
  digitalWrite(PowerOn, HIGH);
  //digitalWrite(Enable_Computers, LOW);
  digitalWrite(Enable12V_MCU, LOW);
  //Serial.println("Not Killed");
  //alarm(0);
  digitalWrite(LED2, LOW);
}

void computerRestart()
{
  TIMSK2 = 0; //Pause Timer2 Interrupt
  //noInterrupts();
  //digitalWrite(Enable_Computers, HIGH);
  delay(5000);
  //digitalWrite(Enable_Computers, LOW);
  //interrupts();
  TIMSK2 |= (1 << TOIE2); //Resume Timer2 Interrupt
}

void readCurrent()
{
  noInterrupts();
  int i;

  for (i = 0; i < 50; i++)
  {
    analogRead(Current_Drive);
    driveCurrent += analogRead(Current_Drive);
    analogRead(Current_Computers);
    computerCurrent += analogRead(Current_Computers);
    delay(2);
  }
  
  driveCurrent /= 50;
  driveCurrent -= 512;
  driveCurrent *= 0.29296875;
  driveCurrent += driveCurrentOffset;
  computerCurrent /= 50;
  computerCurrent -= 512;
  computerCurrent *= 0.29296875;
  computerCurrent += driveCurrentOffset;

  if(driveCurrent >= overCurrentLimit)
  {
    overCurrentCounter ++;
    if(overCurrentCounter > 1)
    {
      overCurrentCond();
    }
  }
  //Serial.println(analogRead(Current_Drive));
  interrupts();
}

void overCurrentCond()
{
  TIMSK2 = 0; //Pause Timer2 Interrupt
  displayState = 3;
  updateDisplay();
  
  noInterrupts();
  //Kill Drive Circuit
  digitalWrite(Enable_Drive, HIGH);
  //digitalWrite(Enable_Computers, LOW);
  digitalWrite(Enable12V_MCU, HIGH);
  //Serial.println("Killed");
  //alarm(1);
  digitalWrite(LED2, HIGH);
  //Enable Drive Circuit temporarily to read current
  while(driveCurrent >= overCurrentLimit)
  {
    digitalWrite(Enable_Drive, LOW);  //Enable Drive
    for (int i = 0; i < 20; i++)
      {
        analogRead(Current_Drive);
        driveCurrent += analogRead(Current_Drive);
        delay(2);
      }
  
    driveCurrent /= 20;
    driveCurrent -= 512;
    driveCurrent *= 0.29296875;
    driveCurrent += driveCurrentOffset;
    digitalWrite(Enable_Drive, HIGH); //Disable Drive
  }
  
  interrupts();
  
  TIMSK2 |= (1 << TOIE2); //Resume Timer2 Interrupt
}

void readVoltages()
{
  noInterrupts();
  int i;
  int temp1;
  int temp2;
  int temp3;
  int temp4;

  for (i = 0; i < 10; i++)
  {
    analogRead(Cell1);
    temp1 += analogRead(Cell1);
    analogRead(Cell2);
    temp2 += analogRead(Cell2);
    analogRead(Cell3);
    temp3 += analogRead(Cell3);
    analogRead(Cell4);
    temp4 += analogRead(Cell4);
    delay(5);
  }

  Cell1_Voltage = float(temp1) / 10;
  Cell2_Voltage = float(temp2) / 10;
  Cell3_Voltage = float(temp3) / 10;
  Cell4_Voltage = float(temp4) / 10;

  Cell1_Voltage /= 243.8095; // 1024/4.2
  Cell2_Voltage /= 121.9048; // 1024/8.4
  Cell2_Voltage -= Cell1_Voltage;
  Cell3_Voltage /= 81.26984; // 1024/12.6
  Cell3_Voltage -= Cell1_Voltage + Cell2_Voltage;
  Cell4_Voltage /= 60.95238; // 1024/16.8
  Total_Voltage  = Cell4_Voltage;
  Cell4_Voltage -= Cell1_Voltage + Cell2_Voltage + Cell3_Voltage;
  interrupts();
}

void alarm(int state)
{
  /*if (state == 1)
  {
    analogWrite(Piezo, 155);
  }
  else
  {
    analogWrite(Piezo, 0);
  }*/
}

/*void printTemperature(DeviceAddress deviceAddress)
{
  float tempC = sensors.getTempC(deviceAddress);
  Serial.print("Temp C: ");
  Serial.print(tempC);
  Serial.print(" Temp F: ");
  Serial.print(DallasTemperature::toFahrenheit(tempC));
}*/

void updateDisplay()
{
  display.clearDisplay();
  if (displayState == 0)
  {
    /*Decor*/
    display.fillRect(0, 0, 127, 20, WHITE);  //Top Bar //83
    //display.fillRect(83, 18, 44, 2, WHITE); //Above Cell Voltage
    display.fillRect(81, 20, 2, 43, WHITE); //Vertical, left of Cell Voltage

    /*Battery Icon*/
    display.fillRect(85, 3, 38, 15, BLACK); //Battery rect
    display.fillRect(123, 7, 2, 7, BLACK);

    //Battery Bars
    if (Total_Voltage >= 12.0) display.fillRect(87, 5, 6, 11, WHITE);
    if (Total_Voltage >= 13.0) display.fillRect(94, 5, 6, 11, WHITE);
    if (Total_Voltage >= 14.0)display.fillRect(101, 5, 6, 11, WHITE);
    if (Total_Voltage >= 15.0)display.fillRect(108, 5, 6, 11, WHITE);
    if (Total_Voltage >= 16.0)display.fillRect(115, 5, 6, 11, WHITE);

    display.setTextSize(2);

    display.setTextColor(BLACK);
    display.setCursor(3, 3);
    display.print(Total_Voltage);
    display.setCursor(63, 3);
    display.print("V");

    //Individual Cell Voltage
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(85, 23);
    display.print("C1:");
    //display.println(Cell1_Voltage);
    display.setCursor(85, 33);
    display.print("C2:");
    //display.println(Cell2_Voltage);
    display.setCursor(85, 43);
    display.print("C3:");
    //display.println(Cell3_Voltage);
    display.setCursor(85, 53);
    display.print("C4:");
    display.print(Cell4_Voltage);

    //Current
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(2, 23);
    display.print("Drive:");
    display.print(driveCurrent);
    display.print("A");
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(2, 33);
    display.print("Comp: ");
    display.print(computerCurrent);
    display.print("A");

    //Temperature
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(2, 43);
    display.print("T1:");
    display.print(temperature1);
    display.print("C");
    display.setCursor(2, 53);
    display.print("T2:");
    display.print(temperature2);
    display.print("C");
    display.display();
  }
  else if(displayState == 1)
  {
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(25, 0);
    display.print("Killed");
    display.display();
    display.setCursor(25, 30);
    display.print(Total_Voltage);
    display.print(" V");
    display.display();
  }
  else if(displayState == 2)
  {
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(17, 0);
    display.print("Good Bye");
    display.setTextSize(1);
    display.setCursor(10, 40);
    display.print("Entering Sleep Mode");
    display.display();

  }
  else if(displayState == 3)
  {
    display.setTextSize(2);
    display.setTextColor(WHITE);
    display.setCursor(15, 0);
    display.print("Over Current!");
    display.display();
    display.setCursor(25, 30);
    display.print("I > 120A");
    display.display();
  }
}

void sendData()
{
  //Start Byte
  //Serial.println(0xEE);
  //Kill Byte
  //Serial.println(killToggle);
  //Cell1 4Bytes
  //Serial.println(Cell1_Voltage, 4);
  //Cell2 4Bytes
  //Serial.println(Cell2_Voltage, 4);
  //Cell3 4Bytes
  //Serial.println(Cell3_Voltage, 4);
  //Cell4 4Bytes
  //Serial.println(Cell4_Voltage, 4);
  //Total Voltage 4Bytes
  //Serial.println(Total_Voltage, 4);
  //Current Computers 4Bytes
  //Serial.println(computerCurrent, 4);
  //Current Drive 4Bytes
  //Serial.println(driveCurrent, 4);
  //Temperature1 4Bytes
  //Serial.println(temperature1,4);
  //Temperature2 4Bytes
  //Serial.println(temperature2,4);
  //Temperature3 4Bytes
  //erial.println(temperature3,4);
}

void updateAll(void)
{
  updateFlag = true;
}

void toggleKS()
{
  digitalWrite(PowerOn, HIGH);
  if(killTimer == 0)
  {
    if (killToggle == true) killToggle = false;
    else if (killToggle == false) killToggle = true;
    killTimer ++;
  }
}

void toggleAuto(){
  canAutoMsg.can_id = 656;
  canAutoMsg.can_dlc = 0;
  MCP2515::ERROR rc = mcp2515.sendMessage(&canAutoMsg);
}



