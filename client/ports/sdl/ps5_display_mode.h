/* SPDX-License-Identifier: Zlib
 * Select up to120Hz from the actual VideoOut inventory, with60Hz fallback.
 * WSI advertises119.88Hz only after OS configuration and vblank verification.
 * Both SDL display reporting and Vulkan surface creation use this policy.
 */
static int PS5_SelectRequestedMode(const VkDisplayModePropertiesKHR *modes,uint32_t count,uint32_t width,uint32_t height)
{
    if(!modes||count==0||count>32||!width||!height)return -1;
    int selected=-1;
    for(uint32_t i=0;i<count;i++){
        VkDisplayModeParametersKHR p=modes[i].parameters;
        if(p.visibleRegion.width!=width||p.visibleRegion.height!=height||p.refreshRate==0||p.refreshRate>120000)continue;
        if(selected<0||p.refreshRate>modes[selected].parameters.refreshRate)selected=(int)i;
    }
    return selected;
}

static int PS5_SelectDisplayMode(const VkDisplayModePropertiesKHR *modes,uint32_t count,VkExtent2D native)
{
    (void)native;
    return PS5_SelectRequestedMode(modes,count,1920,1080);
}

/* -2 means no explicit launcher request; -1 means malformed/unsupported.
 * Never substitute another resolution for an explicit request. */
static int PS5_SelectConfiguredRenderMode(const VkDisplayModePropertiesKHR *modes,uint32_t count,const char *text)
{
    if(!text||!*text)return -2;
    uint32_t w=0,h=0;const char *p=text;
    if(*p<'0'||*p>'9')return -1;
    while(*p>='0'&&*p<='9'){w=w*10+(uint32_t)(*p++-'0');if(w>7680)return -1;}
    if(*p++!='x'||*p<'0'||*p>'9')return -1;
    while(*p>='0'&&*p<='9'){h=h*10+(uint32_t)(*p++-'0');if(h>4320)return -1;}
    if(*p||!w||!h)return -1;
    return PS5_SelectRequestedMode(modes,count,w,h);
}
