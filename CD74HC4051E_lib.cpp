#include "CD74HC4051E_lib.h"

// InputArray -> S2, S1, S0 ; S2, S1 ...
//   		  -> [   IC1  ]  [ IC2  ]....

//NoChips -> number of chips excluding master mux

#define DEBUG 0

bool mux_checkup(uint8_t NoInputs, uint8_t NoChips, uint8_t InputArray[], uint8_t MasterArray[])
{
	uint8_t check_element=0;
	
	for(int index=0;index<sizeof(InputArray);index++)
	{
		check_element=InputArray[index];
		for(int sub_index=0;sub_index<sizeof(InputArray);sub_index++)
		{
			if((check_element==InputArray[sub_index])&&(index!=sub_index))
			{
				Serial.println("ERROR: Multiple declarations of same input pin!");
				return 1;
			}
		}
	}
	
	check_element=0;
	
	for(int index=0;index<sizeof(MasterArray);index++)
	{
		check_element=MasterArray[index];
		for(int sub_index=0;sub_index<sizeof(MasterArray);sub_index++)
		{
			if((check_element==MasterArray[sub_index])&&(index!=sub_index))
			{
				Serial.println("ERROR: Multiple declarations of same master pin!");
				return 1;
			}
		}
	}
	
	// the second part of the clause is because we need to control the enable pin
	if((NoInputs<=(NoChips*8)) || (NoInputs<=(pow(2,sizeof(InputArray)-ceil(sizeof(InputArray)/3)))))
	{
		return 0;
	}
	else
	{
		Serial.println("ERROR: System parameters invalid!");
		Serial.println("Please check number of address pins and chips");
		return 1;
	}
}

uint64_t pin_check(uint8_t NumInputs, uint8_t NumChips, uint8_t InputArray[], uint8_t MasterArray[], uint8_t ReadPin)
{
	uint64_t measurement_array_of_bits=0;
	
	
	//digitalWrite(MasterArray[3],0); //turns on the enable pin of master mux,uncomment if connected already
	for(int master=0;master<NumChips;master++)
	{
		digitalWrite(MasterArray[0],(master&(1<<2))>0);
		digitalWrite(MasterArray[1],(master&(1<<1))>0);
		digitalWrite(MasterArray[2],(master&(1<<0))>0);
	
		#if DEBUG
		Serial.println("MASTER");
		Serial.print("IO");Serial.print(MasterArray[0]);
		Serial.print("  ");Serial.println((master&(1<<2))>0);
		Serial.print("IO");Serial.print(MasterArray[1]);
		Serial.print("  ");Serial.println((master&(1<<1))>0);
		Serial.print("IO");Serial.print(MasterArray[2]);
		Serial.print("  ");Serial.println((master&(1<<0))>0);		
		#endif
		
		for(int index=0;index<8;index++)
		{
			if((index+master*8)<NumInputs)
			{
				digitalWrite(InputArray[master*3+0],(index&(1<<2))>0);
				digitalWrite(InputArray[master*3+1],(index&(1<<1))>0);
				digitalWrite(InputArray[master*3+2],(index&(1<<0))>0);
				
				#if DEBUG
				Serial.println("\nAddress   |     Value");
				Serial.print("IO");
				Serial.print(InputArray[master*3+0]);
				Serial.print(" IO");
				Serial.print(InputArray[master*3+1]);
				Serial.print(" IO");
				Serial.print(InputArray[master*3+2]);
				
				Serial.print(" | ");
				Serial.print((index&(1<<2))>0);
				Serial.print((index&(1<<1))>0);
				Serial.println((index&(1<<0))>0);
				
				Serial.print("Index: ");Serial.print(index);
				Serial.print("  | ");Serial.println(digitalRead(ReadPin));
				#endif
				
				delay(1);
				measurement_array_of_bits+=digitalRead(ReadPin)<<(index+master*8);
			}
		}
	}		
	//digitalWrite(MasterArray[3],1); //turns off the enable pin of master mux, if not connected to GND by default

return measurement_array_of_bits;
}
	