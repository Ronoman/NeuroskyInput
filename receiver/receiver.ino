#include <SoftwareSerial.h>
#include <stdarg.h>
 
#define SYNC   0xAA
#define EXCODE 0x55

int checksum;
unsigned char payload[256];
unsigned char pLength;
unsigned char c;
unsigned char i;

SoftwareSerial stream(2, 3);

void setup() {
    Serial.begin(9600);
    while(!Serial) {}

    stream.begin(9600);
}

void loop() {
    c = stream.read();
    p(c);
    p("\n");
    if( c != SYNC ) return;
    c = stream.read();
    if( c != SYNC ) return;
    
    /* Parse [PLENGTH] byte */
    while( true ) {
        pLength = stream.read();
    }
    if( pLength > 169 ) return;
    
    /* Collect [PAYLOAD...] bytes */
    int count = 0;
    while(count < pLength) {
        strcat(payload, c);
        count += 1;
    }
    
    /* Compute [PAYLOAD...] chksum */
    checksum = 0;
    for( i=0; i<pLength; i++ ) checksum += payload[i];
    checksum &= 0xFF;
    checksum = ~checksum & 0xFF;
    
    /* Parse [CKSUM] byte */
    c = stream.read();
    
    /* Verify [PAYLOAD...] chksum against [CKSUM] */
    if( c != checksum ) return;
    
    /* Since [CKSUM] is OK, parse the Data Payload */
    parsePayload( payload, pLength );
}

void p(char *fmt, ... ){
    char buf[128]; // resulting string limited to 128 chars
    va_list args;
    va_start (args, fmt );
    vsnprintf(buf, 128, fmt, args);
    va_end (args);
    Serial.print(buf);
}

int parsePayload( unsigned char *payload, unsigned char pLength ) {
 
    unsigned char bytesParsed = 0;
    unsigned char code;
    unsigned char len;
    unsigned char extendedCodeLevel;
    int i;
 
    /* Loop until all bytes are parsed from the payload[] array... */
    while( bytesParsed < pLength ) {
 
        /* Parse the extendedCodeLevel, code, and length */
        extendedCodeLevel = 0;
        while( payload[bytesParsed] == EXCODE ) {
            extendedCodeLevel++;
            bytesParsed++;
        }
        code = payload[bytesParsed++];
        if( code & 0x80 ) len = payload[bytesParsed++];
        else              len = 1;
 
        /* TODO: Based on the extendedCodeLevel, code, length,
         * and the [CODE] Definitions Table, handle the next
         * "length" bytes of data from the payload as
         * appropriate for your application.
         */
        p( "EXCODE level: %d CODE: 0x%02X length: %d\n",
                extendedCodeLevel, code, len );
        p( "Data value(s):" );
        for( i=0; i<len; i++ ) {
            p( " %02X", payload[bytesParsed+i] & 0xFF );
        }
        p( "\n" );
 
        /* Increment the bytesParsed by the length of the Data Value */
        bytesParsed += len;
    }
 
    return( 0 );
}
