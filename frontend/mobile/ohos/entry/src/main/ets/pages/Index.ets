@Entry
@Component
struct Index {
  @State message: string = '智学'

  build() {
    Row() {
      Column() {
        Image($r('app.media.app_icon'))
          .width(100)
          .height(100)
          .margin({ bottom: 20 })
        
        Text(this.message)
          .fontSize(32)
          .fontWeight(FontWeight.Bold)
          .margin({ bottom: 10 })
        
        Text('移动端应用')
          .fontSize(16)
          .fontColor('#666666')
      }
      .width('100%')
    }
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
