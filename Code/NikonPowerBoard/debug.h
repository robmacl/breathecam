
void Debug_Init(void);
bool Debug_CharReadyToRead(void);
uint8_t Debug_GetByte(bool blocking);
void Debug_SendByte(uint8_t data);
