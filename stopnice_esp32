#include <Arduino.h>
#include <DFPlayerMini_Fast.h>
#include "CD74HC4051E_lib.h"

#include "BluetoothSerial.h"
#include "esp_bt_device.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

//druga knjiznica za mp3 player
//potrebno installat firetimer.h

#define READ_PIN 39
#define NUM_INPUTS 25
#define NUM_CHIPS 5

#define DEBUG_MAIN 1

#define RXD2 36
#define TXD2 3
DFPlayerMini_Fast myMP3;

// S2, S1, S0
uint8_t master_mux_array[]={17,16,4};
uint8_t input_mux_array[]={/*26,25,1,*/10,9,27,2,5,13,18,0,15,21,19,23,12,14,22};
//pini od mux1 zakomentirani za serial izpis

uint8_t input_remap[25]={9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,1,2,3,4,5,6,7,8};

void printDeviceAddress() {
 
  const uint8_t* point = esp_bt_dev_get_address();
 
  for (int i = 0; i < 6; i++) {
 
    char str[3];
 
    sprintf(str, "%02X", (int)point[i]);
    Serial.print(str);
 
    if (i < 5){
      Serial.print(":");
    }
 
  }
}

void setup()
{
  #if DEBUG_MAIN
  Serial.begin(115200);
  #endif

  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  myMP3.begin(Serial2, false);  
  SerialBT.begin("ESP_stopnice"); //Bluetooth device name

    if(mux_checkup(NUM_INPUTS,NUM_CHIPS,input_mux_array,master_mux_array))
  {
    while(1){}
  }
  
  pinMode(READ_PIN,INPUT);
  
  for(int master=0;master<sizeof(master_mux_array);master++)
  {
    pinMode(master_mux_array[master],OUTPUT);
  }
  
  for(int input=0;input<sizeof(input_mux_array);input++)
  {
    pinMode(input_mux_array[input],OUTPUT);
  }


}

void loop()
{

static bool first=1;
static bool tog=0;
  static uint64_t pins_copy=0;
  static uint64_t pins=0;
  
  pins=digital_pin_check(NUM_INPUTS, NUM_CHIPS,input_mux_array,master_mux_array,READ_PIN);
  if(first)
  {first=0;}
  else
  {
  if(pins!=pins_copy)
  {
    uint64_t change=pins^pins_copy; // XOR checks change of state

    //SerialBT.write(pins);

    for(int q=0;q<  (NUM_INPUTS+1);q++)
    {
      if((change&(1<<q))>0 && !(pins_copy&(1<<q))) 
      {
        myMP3.play(q);

        if(SerialBT.available())
        {
          //q-1 zaradi začetnega indeksa 0
          SerialBT.write(input_remap[q-1]);
          SerialBT.flush();
        }
        else delay(20);

        #if DEBUG_MAIN
        Serial.print("Skladba: ");
        Serial.println(input_remap[q-1]);
       // Serial.println(change);
        #endif
        
      }
    }
    /*
    #if DEBUG_MAIN
    
    for(int debug=0;debug<NUM_INPUTS;debug++)
    {
      Serial.print(pins&(1<<debug));
    }
    Serial.print(uint16_t(pins),BIN);
    Serial.print("  ");
    Serial.print(uint16_t(pins_copy),BIN);
    Serial.print("  ");
    Serial.println(uint16_t(change),BIN);
    #endif
    */
  }
  } 

  //Serial.println(uint16_t(pins),BIN);
  pins_copy=pins;

/*
static int cnt=0;
static bool smer=0;
myMP3.play(1);
delay(100);
if(cnt<14 && !smer){myDFPlayer.volumeUp();cnt++;}
else if(cnt==14 && !smer) smer=1;
else if(cnt>-14 && smer){myDFPlayer.volumeDown();cnt--;}
else if(cnt==-14 && smer) smer=0; 
Serial.println(cnt);Serial.println(smer);
delay(100);
*/
}
