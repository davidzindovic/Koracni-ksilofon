#include <WiFi.h>
#include "time.h"
#include <Preferences.h>

//------------for the user----------
#define DEBUG 0
#define NUM_STEPS 25

//number of days the songs shoud be player:
#define NUM_SONGS_WEEKLY 6

//update after changing holiday arrays:
#define NUM_HOLIDAYS 3

//array of holidays, which should have special song(s)
//the day before
uint8_t holiday_month=[12,02,06];
uint8_t holiday_day=  [00,08,25];
//if holiday_day elemnt is 0, 5 specific songs
//will be played that month. Those 5 songs must be
//the first 5 holiday songs.
//Second written month-> second set of 5 songs...

//holiday song sets should always be first on the SD card,
//accounting for the sequence of holidays
uint8_t holiday_song_set=[0,6,7];
//if song is 0, the software will determine the songs
//from the arrays above

const char* ssid     = "ALHN-F4DA";
const char* password = "c57nvgLUA2";

//-------------end of user input--------------

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = 3600;

const uint8_t day_info=0;

Preferences preferences;

void setup(){

  wifi_init();
  preferences.begin("gpio", false);
  //delay(1000);
  DateAndDayCheck();
}

void loop(){
 // delay(1000);
 // printLocalTime();
}

void DateAndDayCheck(){
  struct tm timeinfo;

  /*
  if(!getLocalTime(&timeinfo)){
    #if DEBUG
    Serial.println("Failed to obtain time");
    #endif
    return;
  }
  */

  bool random_flag=0;
  for(uint8_t hIndex=0;(hIndex<NUM_HOLIDAYS)&&(random_flag==0);hIndex++)
  {
    if((holiday_day[hIndex]==0) && (holiday_month[hIndex]==(timeinfo.tm_mon+1)))
    {EEPROM_PLAYLIST_RANDOMIZING(((hIndex+1)-1)*NUM_SONGS_WEEKLY+1,(hIndex+1)*NUM_SONGS_WEEKLY);random_flag=1;}
    
    else if((holiday_day[hIndex]==(timeinfo.tm_mday)) && (holiday_month[hIndex]==(timeinfo.tm_mon+1)))
    {EEPROM_PLAYLIST_RANDOMIZING(holiday_song_set[hIndex],holiday_song_set[hIndex]);random_flag=1;}
  }
  if(random_flag==0 && timeinfo.tm_wday==1)
  { uint32_t temp_count=0;
    for(uint8_t u=0;u<NUM_HOLIDAYS;u++)
    {
      if(holiday_song_set[u]==0)temp_count+=NUM_SONGS_WEEKLY;
      else temp_count++;
    }
    EEPROM_PLAYLIST_RANDOMIZING(temp_count,0);
    random_flag=1;
  }

  day_info=timeinfo.tm_wday;
  
  #if DEBUG
  Serial.print(timeinfo.tm_wday);
  Serial.print("  ");
  Serial.print(timeinfo.tm_mday);
  Serial.print(".");
  Serial.println(timeinfo.tm_mon+1);
  #endif
}

//TO DO: RANDOMIZER!!!!
void EEPROM_PLAYLIST_RANDOMIZING(uint32_t start_song_index, uint32_t final_song_index)
{ uint16_t random_mode=0;
  
  if(start_song_index==final_song_index)random_mode=1;
  
  
  preferences.putUInt("Day1Start", start_song_index);
  preferences.putUInt("Day1End", final_song_index); 
  
  preferences.putUInt("Day2Start", start_song_index);
  preferences.putUInt("Day2End", final_song_index); 

  preferences.putUInt("Day3Start", start_song_index);
  preferences.putUInt("Day3End", final_song_index); 

  preferences.putUInt("Day4Start", start_song_index);
  preferences.putUInt("Day4End", final_song_index); 

  preferences.putUInt("Day5Start", start_song_index);
  preferences.putUInt("Day5End", final_song_index);

  preferences.putUInt("Day6Start", start_song_index);
  preferences.putUInt("Day6End", final_song_index); 
}

void wifi_init()
{
    #if DEBUG
  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  #endif
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  #if DEBUG
  Serial.println("");
  Serial.println("WiFi connected.");
  #endif
  
  // Init and get the time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  printLocalTime();

  //disconnect WiFi as it's no longer needed
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}

void song_picking()
{
  //if wifi available -> day =index of song sets
  //if not available -> random=index of song sets
}
