// dummy sound stubs for native Win/SDL build — no audio, just satisfy linker
void I_InitSound(int a){ (void)a; }
void I_ShutdownSound(void){}
void I_SetMusicVolume(int a){ (void)a; }
void I_ShutdownMusic(void){}
void I_InitMusic(void){}
int I_MusicIsPlaying(void){ return 0; }
int snd_musicdevice = 0;
void I_UpdateSound(void){}
void I_UpdateSoundParams(int a,int b,int c){ (void)a;(void)b;(void)c; }
int I_GetSfxLumpNum(void* a){ (void)a; return 0; }
void* I_RegisterSong(void* a, int b){ (void)a;(void)b; return 0; }
void I_PlaySong(void* a,int b){ (void)a;(void)b; }
void I_StopSong(void* a){ (void)a; }
void I_UnRegisterSong(void* a){ (void)a; }
void I_PauseSong(void* a){ (void)a; }
void I_ResumeSong(void* a){ (void)a; }
int I_SoundIsPlaying(int a){ (void)a; return 0; }
void I_StopSound(int a){ (void)a; }
int I_StartSound(int a,int b,int c,int d){ (void)a;(void)b;(void)c;(void)d; return 0; }
void I_PrecacheSounds(void* a,int b){ (void)a;(void)b; }
void I_BindSoundVariables(void){}
